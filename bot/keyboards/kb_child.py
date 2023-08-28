from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.cbdata import ActivityChildCFactory, ChildInfoCFactory
from db_service.dbservice import ChildDB, get_navigation_arrows_by_days_of_week
from db_service.pydantic_model import Child_serialize_activities


def ikb_child_total_info(child_id: int):
    """вапвап"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Общий итого',
        callback_data=ChildInfoCFactory(id=child_id, day='False'))
    builder.adjust(1)
    return builder.as_markup()


def ikb_child_activity_list(child_id: int, day=False):
    """Кнопки список заданий ребенка"""
    row = []
    child_info = Child_serialize_activities.validate(
        ChildDB.get_data(child_id=child_id))
    builder = InlineKeyboardBuilder()

    navigation_button = get_navigation_arrows_by_days_of_week(
        child_id=child_id,
        day=day)

    if navigation_button:
        for button in navigation_button:
            builder.button(
                text=button['text'],
                callback_data=ChildInfoCFactory(
                    id=child_id,
                    day=button['day']))

        # берем количество кнопок из ключа первого по списку значений
        row.append(navigation_button[0]['row'])

    for activity in child_info.activities:
        builder.button(
            text=f'{activity.name}',
            callback_data=ActivityChildCFactory(activity_id=activity.id))
        row.append(1)

    builder.adjust(*row)
    return builder.as_markup()
