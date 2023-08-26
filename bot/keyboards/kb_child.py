from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.cbdata import ChildInfoCFactory


def ikb_child_total_info(child_id: int):
    """вапвап"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Общий итого',
        callback_data=ChildInfoCFactory(id=child_id, day='False'))
    builder.adjust(1)
    return builder.as_markup()
