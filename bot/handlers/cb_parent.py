"""Опросник для создания профиля родителя"""
import sys

from aiogram import Router, types, F
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder


sys.path.append("..")
from tg_bot import my_bot  # noqa: E402
from bot.statesgroup import AddParentStatesGroup  # noqa: E402
from bot.keyboards.kb_general import ikb_gender  # noqa: E402
from bot.keyboards.kb_parent import ikb_parent_children, \
    kb_share_phone  # noqa: E402
from bot.cbdata import ActivityDayCompletionNotificationCFactory, \
    GenderCFactory, TickChangeActivityCFactory  # noqa: E402
from db_service.service import get_child_gender_emoji, valid_name, \
    valid_number  # noqa: E402
from db_service.dbservice import ActivityDayDB, ChildDB, ParentDB, \
    add_parent_and_child  # noqa: E402
from db_service.pydantic_model import Parent_and_child  # noqa: E402


router = Router()


def ikb_parent() -> types.InlineKeyboardButton:
    """Кнопка продолжить с одной кнопкой"""
    builder = InlineKeyboardBuilder()
    builder.button(text='Продолжить', callback_data='cb_parent')
    builder.adjust(1)
    return builder.as_markup()


def ikb_confirm_execution(activity_day_id) -> types.InlineKeyboardButton:
    """Кнопка подтвердить выполнение задания"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Подтвердить выполнение',
        callback_data=TickChangeActivityCFactory(
            activity_day_id=activity_day_id))
    builder.adjust(1)
    return builder.as_markup()


@router.callback_query(ActivityDayCompletionNotificationCFactory.filter())
async def cb_notification_completion_of_activity_day(
        callback: types.CallbackQuery,
        callback_data: ActivityDayCompletionNotificationCFactory):
    """Отправка сообщений о выполнении задания ребенком
    с информацией о задании и кнопкой подтверждения"""
    activity_name = ActivityDayDB.get_activity_name(
        activity_day_id=callback_data.activity_day_id)

    parents_bot_user_id = ParentDB.get_all_bot_users_id(
        child_id=callback_data.child_id)

    child_name = ChildDB.get_name(child_id=callback_data.child_id)

    try:
        for one_id in parents_bot_user_id:
            await my_bot.send_message(
                one_id,
                text=f'{child_name}, просит подтвердить выполнения задания'
                f' - {activity_name}',
                reply_markup=ikb_confirm_execution(
                    activity_day_id=callback_data.activity_day_id))
    except:
        pass
    await callback.message.edit_text(text='Уведомление отправлено')


@router.callback_query(Text('cb_parent'))
async def cb_add_parent(
        callback: types.CallbackQuery, state: FSMContext) -> None:
    """Первый пункт опросника по регистрации ребенка"""
    # Получем его данные
    parent_data = ParentDB.is_bot_user_id(int(callback.from_user.id))

    if parent_data is None:  # если родителя нет, то добавляем
        await callback.message.answer(
            text="Для работы бота нужен Ваш номер телефона",
            reply_markup=kb_share_phone())
        await state.set_state(AddParentStatesGroup.parent_number)

    else:  # если есть запускаем меню работы с ним
        await callback.message.answer(
            text='Выберите ребенка',
            reply_markup=ikb_parent_children(
                bot_user_id=int(callback.from_user.id)))


@router.message(F.contact,
                AddParentStatesGroup.parent_number)
async def cb_add_parent_number(
        message: types.Message, state: FSMContext) -> None:
    """Добавление данных родителя - 2 этап получение номера телефона"""
    contact = message.contact  # Получем его данные
    fullname = valid_name(contact)
    phone_number = valid_number(contact.phone_number)
    parent = ParentDB.get_or_update_data_by_phone_number(
        phone_number=phone_number,
        bot_user_id=message.from_user.id)

    if parent:  # Если номер телефона есть в БД
        await message.answer(
            text='Выберите ребенка',
            reply_markup=ikb_parent_children(
                bot_user_id=int(message.from_user.id))
            )
    else:
        await message.answer(
            f"Спасибо, {fullname}.\n",
            reply_markup=types.ReplyKeyboardRemove())

        await state.update_data(phone_number=phone_number)
        await state.update_data(name=f'{fullname}')
        await state.update_data(bot_user_id=contact.user_id)

        data = await state.get_data()  # Загружаем данные из FSM
        await message.answer(
            f"Ваш номер {data['phone_number']} был получен. \n"
            f"Выберите ваш пол",
            reply_markup=ikb_gender())
        await state.set_state(AddParentStatesGroup.gender)


@router.callback_query(GenderCFactory.filter(), AddParentStatesGroup.gender)
async def cb_add_parent_gender(callback: types.CallbackQuery,
                               callback_data: GenderCFactory,
                               state: FSMContext) -> None:
    """Добавление данных родителя - 3 этап пол родителя"""
    # Standard ISO/IEC 5218 0 -not known, 1 -Male, 2 -Female, 9 -Not applicable
    await state.update_data(sex=int(callback_data.gender))
    # TODO: Добавить удаление inline кнопок
    await callback.message.edit_text(
        text='Введите номер телефона ребенка')
    await state.set_state(AddParentStatesGroup.child_phone)


@router.message(AddParentStatesGroup.child_phone)
async def add_parent_child_phone(message: types.Message, state: FSMContext) -> None:
    """Добавление данных родителя - 4 этап номер телефона ребенка"""
    child_number = valid_number(message.text)
    if child_number:
        await state.update_data(child_number=child_number)
        await message.answer(
            text=f'Для номера: <b>{child_number}</b> введите имя ребенка')

        await state.set_state(AddParentStatesGroup.child_name)
    else:
        await message.reply(
            text=f'Номер - "{message.text}" не распознан\n'
            f'Пожалуйста введите номер телефон в формате 7 987 654 32 10')


@router.message(AddParentStatesGroup.child_name)
async def cb_add_parent_child_name(
        message: types.Message, state: FSMContext) -> None:
    """Добавление данных родителя - 5 этап имя ребенка"""
    await state.update_data(child_name=message.text)
    await message.answer(
        f'Выберите пол - {message.text}',
        reply_markup=ikb_gender())
    await state.set_state(AddParentStatesGroup.child_gender)


@router.callback_query(GenderCFactory.filter(),
                       AddParentStatesGroup.child_gender)
async def cb_add_parent_child_gender(
        callback: types.CallbackQuery,
        callback_data: GenderCFactory,
        state: FSMContext) -> None:
    """Добавление данных родителя - 6 этап пол ребенка"""
    # Standard ISO/IEC 5218 0 -not known, 1 -Male, 2 -Female, 9 -Not applicable
    await state.update_data(child_sex=int(callback_data.gender))
    data = await state.get_data()
    info = Parent_and_child.validate(data)
    info_db = add_parent_and_child(info)
    await callback.message.edit_text(
        text=f'Добавили данные {info_db}',
        reply_markup=ikb_parent())  # TODO: Добавить удаление inline кнопок
    await state.clear()
