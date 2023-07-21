"""Опросник для добавления еще одного родителя"""
import sys

from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.filters.text import Text
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder


sys.path.append("..")
from bot.statesgroup import AddOneMoreParentStatesGroup, AddParentStatesGroup
from bot.keyboards.kb_general import ikb_gender
from bot.keyboards.kb_parent import ikb_parent_children, kb_share_phone
from bot.cbdata import ChildCallbackFactory, GenderCallbackFactory
from db_service.service import get_child_gender_emoji, valid_number
from db_service.dbservice import Child_DB, Parent_DB, add_parent_and_child, is_parent_in_db
from db_service.pydantic_model import Parent_and_child, Parent_base_and_child, Children_in_parent_base


router = Router()


@router.callback_query(Text('cb_add_one_more_parent'))
async def cb_add_one_more_parent(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Первый пункт опросника по добавлению еще одного родителя"""
    await callback.message.answer(text="Введите имя еще одного родителя")
    await state.set_state(AddOneMoreParentStatesGroup.parent_name)


@router.message(AddOneMoreParentStatesGroup.parent_name)
async def cb_add_one_more_parent_name(message: types.Message, state: FSMContext) -> None:
    """Добавление данных родителя - 2 этап имя родителя"""
    await state.update_data(name=message.text)
    await message.answer(f'Выберите пол - {message.text}', reply_markup=ikb_gender())
    await state.set_state(AddOneMoreParentStatesGroup.gender)


@router.callback_query(GenderCallbackFactory.filter(), AddOneMoreParentStatesGroup.gender)
async def cb_add_one_more_parent_gender(callback: types.CallbackQuery,
                               callback_data: GenderCallbackFactory,
                               state: FSMContext) -> None:
    """Добавление данных родителя - 3 этап пол родителя"""
    await state.update_data(gender=int(callback_data.gender)) # Standard ISO/IEC 5218 0 - not known, 1 - Male, 2 - Female, 9 - Not applicable
    data = await state.get_data()  # Загружаем данные из FSM
    await callback.message.answer(f'Введите номер телефона <b>{data["name"]}</b>:')
    await state.set_state(AddOneMoreParentStatesGroup.parent_number)


@router.message(AddOneMoreParentStatesGroup.parent_number)
async def cb_add_one_more_parent_phone(message: types.Message, state: FSMContext) -> None:
    """Добавление данных родителя - 4 этап номер телефона родителя"""
    parent_number = valid_number(message.text)
    if parent_number:
        parent_data = is_parent_in_db(int(message.from_user.id)) # Получем его данные
        all_children_id = Child_DB.get_all_children_id(parent_id=parent_data['id'])
        await state.update_data(phone=parent_number)
        await state.update_data(all_children_id=all_children_id)
        data = await state.get_data()
        Parent_DB.add_one_more_parent(data=data)
        await message.answer(f'Родитель добавлен', reply_markup=ikb_parent_children(bot_user_id=message.from_user.id))
    else:
        await message.reply(f'Номер - "{message.text}" не распознан\nПожалуйста введите номер телефон в формате 7 987 654 32 10')

