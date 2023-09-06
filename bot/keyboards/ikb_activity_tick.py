from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.cbdata import ActivityCallbackFactory, BaseChildCFactory, TickChangeActivityCFactory
from db_service.dbservice import ChildDB, get_weekly_navigation_arrows
from db_service.pydantic_model import Activity_serialize


def ikb_activity_tick(activity_id: int, day=False):
    """Одно задание по дням недели и возможность отметить выполнения по дням"""
    activity = Activity_serialize.validate(
        ChildDB.get_activity_one(activity_id=activity_id, day=day))
    builder = InlineKeyboardBuilder()
    # Сортировка по дате
    days = sorted(activity.activity_days, key=lambda x: x.day)
    row = []
    for one_day in days:
        if one_day.is_done:
            is_done = '✅'
        else:
            is_done = '❌'
        builder.button(
            text=f'{one_day.day.strftime("%a %d %b")} {is_done}',
            callback_data='cb_activity_day_one'
            )
        builder.button(
            text='изменить 🔄',
            callback_data=TickChangeActivityCFactory(
                activity_day_id=one_day.id))
        row.append(2)

    # Получаем данные по пред. неделям если есть добавляем кнопки
    navigation_button = get_weekly_navigation_arrows(
        child_id=activity.child_id,
        day=day
        )
    if navigation_button:  # Если есть пред. дни недели доб. кнопки навигации
        for button in navigation_button:
            builder.button(
                text=button['text'],
                callback_data=ActivityCallbackFactory(
                    activity_id=activity_id,
                    tick='yes',
                    day=button['day'])
                )
        # берем количество кнопок из ключа первого по списку значений
        row.append(navigation_button[0]['row'])
    builder.button(
        text='Перейти списку заданий',
        callback_data=BaseChildCFactory(id=activity.child_id, day=False))
    row.append(1)
    builder.adjust(*row)
    return builder.as_markup()
