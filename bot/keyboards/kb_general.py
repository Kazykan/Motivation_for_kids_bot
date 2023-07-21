import sys
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

sys.path.append("..")
from bot.cbdata import GenderCallbackFactory


def ikb_gender():
    """Кнопки пол человека"""
    builder = InlineKeyboardBuilder()
    builder.button(text='Муж. 👨', callback_data=GenderCallbackFactory(gender='1'))
    builder.button(text='Жен. 👩', callback_data=GenderCallbackFactory(gender='2'))
    builder.adjust(2)
    return builder.as_markup()





# def ikb_gender() -> types.InlineKeyboardMarkup:
#     """Кнопки пол человека"""
#     buttons = [
#         [
#             types.InlineKeyboardButton(text='Муж. 👨',
#                 callback_data=GenderCallbackFactory(gender='1')),
#             types.InlineKeyboardButton(text='Жен. 👩',
#                 callback_data=GenderCallbackFactory(gender='2')),
#         ],
#     ]
#     inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
#     return inline_keyboard