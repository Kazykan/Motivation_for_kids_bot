from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.cbdata import BaseChildCFactory


def ikb_list_of_activity(child_id: int) -> types.InlineKeyboardMarkup:
    """Кнопка перейти к списку заданий"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Перейти списку заданий',
        callback_data=BaseChildCFactory(id=child_id, day=False))
    builder.adjust(1)
    return builder.as_markup()
