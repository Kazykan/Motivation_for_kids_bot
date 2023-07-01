"""Опросник для создания профиля родителя"""
import sys

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher, types
from pydantic import BaseModel

sys.path.append("..")
from db_service.service import valid_number
from db_service.dbservice import add_parent_and_child, is_parent_in_db
from db_service.pydantic_model import Parent_and_child, Parent_base, Children_in_parent_base


def ikb_sex() -> types.InlineKeyboardMarkup:
    """Кнопки пол человека"""
    ikb = types.InlineKeyboardMarkup(row_width=2, inline_keyboard=[
        [types.InlineKeyboardButton(text='Муж. 👨', callback_data='cb_male'),
         types.InlineKeyboardButton(text='Жен. 👩', callback_data='cb_female')],
    ], markup=types.ReplyKeyboardRemove())
    return ikb


def kb_share_phone() -> types.KeyboardButton:
    button_phone = types.KeyboardButton(text="Поделиться номером ☎️", request_contact=True)
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(button_phone)
    return keyboard


def ikb_parent_children(parent_data):
    """Кнопка со списком детей"""
    data = Parent_base.parse_obj(parent_data)
    ikb = types.InlineKeyboardMarkup()
    ikb.row_width = 1
    ikb.markup = types.ReplyKeyboardRemove()
    for child in data.children:
        ikb.add(types.InlineKeyboardButton(text=f'{child.name} - тел.: 7···{child.phone[5:]}', callback_data=f'cb_child_{child.id}'))
    return ikb


class AddParentStatesGroup(StatesGroup):
    """Машина состояний для работы опросника по добавлению добавлению Родителя и детей"""
    parent_number = State()
    sex = State()
    child_phone = State()
    child_name = State()
    child_sex = State()


async def cb_add_parent(callback: types.CallbackQuery) -> None:
    """Первый пункт опросника по добавлению Родителя"""
    await callback.message.delete()
    parent_data = is_parent_in_db(int(callback.from_user.id)) # Получем его данные
    if parent_data is None:  # если родителя нет, то добавляем
        await callback.message.answer(text="Для работы бота нужен Ваш номер телефона, нажмите внизу кнопку - Поделиться номером",
                                  reply_markup=kb_share_phone())
        await AddParentStatesGroup.parent_number.set()
    else: # если есть запускаем меню работы с ним
        await callback.message.answer(text='Выберите ребенка', reply_markup=ikb_parent_children(parent_data))



async def cb_add_parent_number(message: types.Message, state: FSMContext) -> None:
    """Добавление данных родителя - 2 этап получение номера телефона"""
    contact = message.contact  # Получем его данные
    await message.delete()
    await message.answer(f"Спасибо, {contact.full_name}.\n", reply_markup=types.ReplyKeyboardRemove())
    async with state.proxy() as data:
        data['phone_number'] = valid_number(contact.phone_number)
        data['name'] = contact.full_name
        data['bot_user_id'] = contact.user_id
    await message.answer(f"Ваш номер {contact.phone_number} был получен. \n"
                         f"Ваш id {contact.user_id}. \n"
                         f"Выберите ваш пол",
                         reply_markup=ikb_sex())
    await AddParentStatesGroup.sex.set()


async def cb_add_parent_sex(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Добавление данных родителя - 3 этап пол родителя"""
    await callback.message.delete()
    async with state.proxy() as data:
        if callback.data == 'cb_male':  # Получаем значение из callback_query_handler какая именно кнопка нажата
            data['sex'] = 1 # Standard ISO/IEC 5218 0 - not known, 1 - Male, 2 - Female, 9 - Not applicable
        else: data['sex'] = 2
    await callback.message.answer(f'Введите номер телефона ребенка', reply_markup=types.ReplyKeyboardRemove()) # TODO: Добавить удаление inline кнопок
    await AddParentStatesGroup.child_phone.set()


async def cb_add_parent_child_phone(message: types.Message, state: FSMContext) -> None:
    """Добавление данных родителя - 4 этап номер телефона ребенка"""
    await message.delete()
    child_number = valid_number(message.text)
    if child_number:
        async with state.proxy() as data:
            data['child_number'] = child_number
        await message.answer(f'Для номера: {data["child_number"]} введите имя ребенка')
        await AddParentStatesGroup.child_name.set()
    else:
        await message.reply(f'Номер - "{message.text}" не распознан\nПожалуйста введите номер телефон в формате 7987 654 32 10')


async def cb_add_parent_child_name(message: types.Message, state: FSMContext) -> None:
    """Добавление данных родителя - 5 этап имя ребенка"""
    async with state.proxy() as data:
        data['child_name'] = message.text
    await message.answer(f'Выберите пол - {data["child_name"]}', reply_markup=ikb_sex())
    await AddParentStatesGroup.child_sex.set()


async def cb_add_parent_child_sex(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Добавление данных родителя - 6 этап пол ребенка"""
    await callback.message.delete()
    async with state.proxy() as data:
        if callback.data == 'cb_male':  # Получаем значение из callback_query_handler какая именно кнопка нажата
            data['child_sex'] = 1 # Standard ISO/IEC 5218 0 - not known, 1 - Male, 2 - Female, 9 - Not applicable
        else: data['child_sex'] = 2
    info = Parent_and_child.parse_obj(data._data)
    info_db = add_parent_and_child(info)
    await callback.message.answer(f'Добавили данные {info_db}') # TODO: Добавить удаление inline кнопок
    await state.finish()


def register_cb_handlers_add_parent(dp: Dispatcher):
    dp.register_callback_query_handler(cb_add_parent,
                                       text_contains='cb_parent',
                                       state='*')
    # регистрация след этапа машины состояний, в случае если передали телефонный номер
    dp.register_message_handler(cb_add_parent_number,
                                content_types=types.ContentType.CONTACT,
                                state=AddParentStatesGroup.parent_number)
    dp.register_callback_query_handler(cb_add_parent_sex,
                                       text_contains='cb_male',
                                       state=AddParentStatesGroup.sex)  # TODO: два одинаковых колбека cb_male и cb_female посмотреть как их можно объединить
    dp.register_callback_query_handler(cb_add_parent_sex,
                                       text_contains='cb_female',
                                       state=AddParentStatesGroup.sex)
    dp.register_message_handler(cb_add_parent_child_phone, state=AddParentStatesGroup.child_phone)
    dp.register_message_handler(cb_add_parent_child_name, state=AddParentStatesGroup.child_name)
    dp.register_callback_query_handler(cb_add_parent_child_sex,
                                       text_contains='cb_male',
                                       state=AddParentStatesGroup.child_sex)  # TODO: два одинаковых колбека cb_male и cb_female посмотреть как их можно объединить
    dp.register_callback_query_handler(cb_add_parent_child_sex,
                                       text_contains='cb_female',
                                       state=AddParentStatesGroup.child_sex)