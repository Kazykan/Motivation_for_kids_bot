from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.cbdata import ActivityCallbackFactory, AddActivityCFactory, \
    ChangeOneWeekOnActivityCFactory, \
    DeleteActivityCFactory, EditActivityCFactory
from db_service.dbservice import ChildDB
from db_service.pydantic_model import Child_serialize_activities


def ikb_edit_activity_menu(child_id: int, day=False):
    """Кнопки список заданий ребенка (выбрать дни недели, удалить)
    + кнопка добавить еще задание"""
    row = []
    child_info = Child_serialize_activities.validate(
        ChildDB.get_data(child_id=child_id)
        )
    builder = InlineKeyboardBuilder()

    for activity in child_info.activities:
        builder.button(
            text=f'{activity.name}',
            callback_data=ActivityCallbackFactory(
                activity_id=activity.id, tick='no')
            )
        builder.button(
            text='📅',
            callback_data=ChangeOneWeekOnActivityCFactory(
                week_id=1,
                activity_id=activity.id,
                edit=False))
        builder.button(
            text='🗑',
            callback_data=DeleteActivityCFactory(
                activity_id=activity.id,
                second_stage='no'))
        builder.button(
            text='📝',
            callback_data=EditActivityCFactory(activity_id=activity.id)
            )
        row.append(4)
    row.append(2)
    builder.button(
        text='➕ Добавить задание',
        callback_data=AddActivityCFactory(child_id=child_info.id)
        )
    builder.button(text='🔙 Назад', callback_data="cb_parent")
    builder.adjust(*row)
    return builder.as_markup()