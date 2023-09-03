from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.cbdata import ActivityCFactory, AddActivityCFactory, \
    BaseChildCFactory, ChangeOneWeekOnActivityCFactory, \
    DeleteActivityCFactory, EditActivityCFactory
from db_service.dbservice import ChildDB, get_navigation_arrows_by_days_of_week
from db_service.pydantic_model import Child_serialize_activities


def ikb_child_menu(child_id: int, day=False):
    """Кнопки список заданий ребенка (отметить, выбрать дни недели, удалить)
    + кнопка добавить еще задание"""
    row = []
    child_info = Child_serialize_activities.validate(
        ChildDB.get_data(child_id=child_id)
        )
    builder = InlineKeyboardBuilder()
    navigation_button = get_navigation_arrows_by_days_of_week(
        child_id=child_id,
        day=day
        )
    if navigation_button:  # Если есть пред. дни недели доб. кнопки навигации
        for button in navigation_button:
            builder.button(
                text=button['text'],
                callback_data=BaseChildCFactory(id=child_id, day=button['day'])
                )
        # берем количество кнопок из ключа первого по списку значений
        row.append(navigation_button[0]['row'])
    for activity in child_info.activities:
        builder.button(
            text=f'{activity.name}',
            callback_data=ActivityCFactory(activity_id=activity.id, tick='no')
            )
        builder.button(
            text='✔️',
            callback_data=ActivityCFactory(activity_id=activity.id, tick='yes')
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
        row.append(5)
    row.append(2)
    builder.button(
        text='➕ Добавить задание',
        callback_data=AddActivityCFactory(child_id=child_info.id)
        )
    builder.button(text='🔙 Назад', callback_data="cb_parent")
    builder.adjust(*row)
    return builder.as_markup()
