import sys
from aiogram.utils.keyboard import InlineKeyboardBuilder

sys.path.append("..")
from bot.cbdata import GenderCFactory  # noqa: E402


def ikb_gender():
    """Кнопки пол человека"""
    builder = InlineKeyboardBuilder()
    builder.button(text='Муж. 👨', callback_data=GenderCFactory(gender='1'))
    builder.button(text='Жен. 👩', callback_data=GenderCFactory(gender='2'))
    builder.adjust(2)
    return builder.as_markup()
