
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.cbdata import BaseChildCFactory
from db_service.dbservice import ParentDB
from db_service.pydantic_model import Parent_base_and_child
from db_service.service import get_child_gender_emoji



def kb_share_phone() -> types.KeyboardButton:
    button_phone = [[types.KeyboardButton(text="Поделиться номером ☎️", request_contact=True)]]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
        input_field_placeholder='Нажмите поделиться номером...',
        keyboard=button_phone)
    return keyboard



def ikb_parent_children(bot_user_id):
    """Кнопка со списком детей + добавить еще одного ребенка"""
    parent_data = ParentDB.is_bot_user_id(bot_user_id) # Получем его данные
    data = Parent_base_and_child.validate(parent_data)
    builder = InlineKeyboardBuilder()
    row = []
    for child in data.children:
        builder.button(text=f'{child.name} {get_child_gender_emoji(child.sex)}',
            callback_data=BaseChildCFactory(id=child.id, day=False))
        row.append(1)
    row.append(2)
    builder.button(text='Доб ребенка 🐰', callback_data='cb_add_child')
    builder.button(text='Доб родителя 🐻', callback_data='cb_add_one_more_parent')  
    builder.adjust(*row)
    return builder.as_markup()