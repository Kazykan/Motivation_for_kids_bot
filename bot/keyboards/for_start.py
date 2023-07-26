from aiogram import types


def ikb_start() -> types.InlineKeyboardButton:
    """Кнопки первые: выбор родитель или ребенок"""
    buttons = [
        [
            types.InlineKeyboardButton(text="Родитель 🐻", callback_data="cb_parent"),
            types.InlineKeyboardButton(text="Ребенок 🐰", callback_data="cb_child_info")
        ],
        [types.InlineKeyboardButton(text="Ссылка на видео про мотивацию",
                                    url='https://www.youtube.com/watch?v=6x6B0bmtmjI')]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard