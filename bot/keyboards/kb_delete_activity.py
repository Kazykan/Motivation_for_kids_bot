from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.cbdata import BaseChildCFactory, DeleteActivityCFactory


def ikb_delete_activity(
        activity_id: int, child_id: int) -> types.InlineKeyboardMarkup:
    """Кнопка перейти к списку заданий"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Да',
        callback_data=DeleteActivityCFactory(
            activity_id=activity_id,
            second_stage='yes'))
    builder.button(
        text='Нет',
        callback_data=BaseChildCFactory(id=child_id, day=False))
    builder.adjust(2)
    return builder.as_markup()
