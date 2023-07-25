"""Опросник для создания профиля родителя"""
import sys

from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.filters.text import Text
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder



sys.path.append("..")
from bot.keyboards.kb_parent import kb_share_phone
from bot.cbdata import ActivityChildCallbackFactory
from db_service.service import activity_to_text, get_child_gender_emoji, valid_number
from db_service.dbservice import Child_DB, add_parent_and_child, report_table_child
from db_service.pydantic_model import Activity_serialize, Child_serialize_activities


router = Router()


def ikb_child_total_info(child_id: int):
    """вапвап"""
    builder = InlineKeyboardBuilder()
    builder.button(text='Общий итого',
                        callback_data='cb_child')
    builder.adjust(1)
    return builder.as_markup()


def ikb_child_activity_list(child_id: int):
    """Кнопки список заданий ребенка"""
    child_info = Child_serialize_activities.validate(Child_DB.get_data(child_id=child_id))
    builder = InlineKeyboardBuilder()
    for activity in child_info.activities:
        builder.button(text=f'{activity.name}',
                        callback_data=ActivityChildCallbackFactory(
                        activity_id=activity.id))
    builder.button(text='Общий итого',
                        callback_data='cb_child')
    builder.adjust(1)
    return builder.as_markup()


class AddChildStatesGroup(StatesGroup):
    """Машина состояний для работы опросника по регистрации Ребенка"""
    child_phone = State()


@router.callback_query(ActivityChildCallbackFactory.filter())
async def cb_child_activity_fab(callback: types.CallbackQuery,
                                callback_data: ActivityChildCallbackFactory) -> None:
    """Подробности про одно задание + отметка о выполнении"""
    activity = Activity_serialize.validate(
        Child_DB.get_activity_one(activity_id=int(callback_data.activity_id)))
    info = activity_to_text(activity)
    await callback.message.edit_text(text=f'<code>{info}\n</code>',
                                        reply_markup=ikb_child_total_info(child_id=activity.child_id))


@router.callback_query(Text('cb_child'))
async def cb_add_child(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Первый пункт опросника по регистрации Ребенка"""
    child_data = Child_DB.check_is_bot_user_id(bot_user_id=int(callback.from_user.id)) # Получем его данные
    if child_data is None:  # если ребенка нет, то добавляем
        await callback.message.answer(text="Для работы бота нужен Ваш номер телефона",
                                  reply_markup=kb_share_phone())
        await state.set_state(AddChildStatesGroup.child_phone)
    else: # если есть запускаем меню работы с ним
        child_info = Child_serialize_activities.validate(child_data)
        info = report_table_child(child_info)
        await callback.message.edit_text(text=f'<code>{info}\n</code>\n',
                            reply_markup=ikb_child_activity_list(child_id=child_info.id))


@router.message(F.contact,
                AddChildStatesGroup.child_phone)
async def cb_add_parent_number(message: types.Message, state: FSMContext) -> None:
    """Добавление данных ребенка - 2 этап получение номера телефона"""
    child_number = valid_number(message.contact.phone_number)  # Получем его данные
    child_data = Child_DB.check_is_phone(child_number=child_number)
    if child_data:  # Если данные найдены
        child_info = Child_serialize_activities.validate(child_data)
        await message.answer(text=f'{child_info}')
        if child_info.bot_user_id is None: # Если нет bot_user_id обновляем данные
            Child_DB.update(child_id=child_info.id, bot_user_id=message.from_user.id)
        info = report_table_child(child_info)
        await message.answer(text=f'<code>{info}\n</code>\n {child_info}',
                            reply_markup=ikb_child_activity_list(child_id=child_info.id))
