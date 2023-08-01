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
from bot.cbdata import ActivityChildCFactory, ActivityDayCompletionNotificationCFactory, ChildInfoCFactory
from db_service.service import activity_to_text, convert_date, valid_number
from db_service.dbservice import ActivityDayDB, ChildDB, get_navigation_arrows_by_days_of_week, report_table_child
from db_service.pydantic_model import Activity_serialize, Child_serialize_activities


router = Router()


class AddChildStatesGroup(StatesGroup):
    """Машина состояний для работы опросника по регистрации Ребенка"""
    child_phone = State()


def ikb_child_total_info(child_id: int):
    """вапвап"""
    builder = InlineKeyboardBuilder()
    builder.button(text='Общий итого',
            callback_data=ChildInfoCFactory(id=child_id, day='False'))
    builder.adjust(1)
    return builder.as_markup()


def ikb_child_completion_notification_for_parents(child_id: int, activity_day_id: int):
    """Кнопка отправки подтверждения о выполнении задания"""
    builder = InlineKeyboardBuilder()
    builder.button(text=f'🆗 я выполнил это задние',
                   callback_data=ActivityDayCompletionNotificationCFactory(
        child_id=child_id,
        activity_day_id=activity_day_id,
        parent='no'))
    builder.button(text='🔙 Назад',
            callback_data=ChildInfoCFactory(id=child_id, day='False'))
    builder.adjust(1)
    return builder.as_markup()


def ikb_child_activity_list(child_id: int, day=False):
    """Кнопки список заданий ребенка"""
    row = []
    child_info = Child_serialize_activities.validate(ChildDB.get_data(child_id=child_id))
    builder = InlineKeyboardBuilder()

    navigation_button = get_navigation_arrows_by_days_of_week(child_id=child_id, day=day)
    if navigation_button:
        for button in navigation_button:
            builder.button(text=button['text'],
                    callback_data=ChildInfoCFactory(id=child_id, day=button['day']))
        row.append(navigation_button[0]['row'])  # берем количество кнопок из ключа первого по списку значений

    for activity in child_info.activities:
        builder.button(text=f'{activity.name}',
                        callback_data=ActivityChildCFactory(
                        activity_id=activity.id))
        row.append(1)
    builder.adjust(*row)
    return builder.as_markup()


@router.callback_query(ActivityChildCFactory.filter())
async def cb_child_fab(callback: types.CallbackQuery,
                                callback_data: ActivityChildCFactory) -> None:
    """Подробности про одно задание + отметка о выполнении"""
    activity = Activity_serialize.validate(
        ChildDB.get_activity_one(activity_id=int(callback_data.activity_id)))
    info = activity_to_text(activity)
    activity_day_these_day = ActivityDayDB.there_is_for_today(activity_id=int(callback_data.activity_id))  # Есть эта активность на этот день
    print(f'activity_day_these_day   ---- {activity_day_these_day}')
    if activity_day_these_day: # Если есть добавляем кнопку
        await callback.message.edit_text(
            text=f'<code>{info}\n</code>'
            f'Если вы выполнили это задание <b>сегодня</b> нажмите кнопку ниже, вашим родителям придет уведомление и они решат сделали вы его или нет',
            reply_markup=ikb_child_completion_notification_for_parents(
                child_id=activity.child_id, activity_day_id=activity_day_these_day))
    else:
        await callback.message.edit_text(text=f'<code>{info}\n</code>',
                                        reply_markup=ikb_child_total_info(child_id=activity.child_id))


@router.callback_query(ChildInfoCFactory.filter())
async def cb_child_info_fab(callback: types.CallbackQuery,
                            callback_data: ChildInfoCFactory) -> None:
    """Список заданий ребенка + отчет"""
    child_info = Child_serialize_activities.validate(ChildDB.get_data(child_id=callback_data.id))
    info = report_table_child(child_info, day=convert_date(callback_data.day))
    await callback.message.edit_text(text=f'<code>{info}\n</code>\n',
        reply_markup=ikb_child_activity_list(child_id=int(callback_data.id), day=callback_data.day))


@router.callback_query(Text('cb_child_info'))
async def cb_add_child(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Первый пункт опросника по регистрации Ребенка"""
    child_data = ChildDB.check_is_bot_user_id(bot_user_id=int(callback.from_user.id)) # Получем его данные
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
    child_data = ChildDB.check_is_phone(child_number=child_number)
    if child_data:  # Если данные найдены
        child_info = Child_serialize_activities.validate(child_data)
        await message.answer(text=f'{child_info}')
        if child_info.bot_user_id is None: # Если нет bot_user_id обновляем данные
            ChildDB.update(child_id=child_info.id, bot_user_id=message.from_user.id)
        info = report_table_child(child_info)
        await message.answer(text=f'<code>{info}\n</code>\n {child_info}',
                            reply_markup=ikb_child_activity_list(child_id=child_info.id))
