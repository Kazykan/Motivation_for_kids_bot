from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.cbdata import EditActivityOptionsCFactory


def ikb_activity_edit_list(activity_id: int):
    """Кнопки с пунктами для редактирования"""
    builder = InlineKeyboardBuilder()
    activity_dict = {
        'name': 'название',
        'title': 'описание',
        'percent_complete': 'процент вып.',
        'cost': 'стоимость'}
    for key, value in activity_dict.items():
        builder.button(
            text=f'{value}',
            callback_data=EditActivityOptionsCFactory(
                activity_id=activity_id,
                field=key,
                description=value)
            )
    builder.button(text='🔙 Назад', callback_data="cb_parent")
    builder.adjust(1)
    return builder.as_markup()
