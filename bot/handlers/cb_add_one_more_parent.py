"""Опросник для добавления еще одного родителя"""
import sys

from aiogram import Router, types
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext



sys.path.append("..")
from bot.statesgroup import AddOneMoreParentSGroup
from bot.keyboards.kb_general import ikb_gender
from bot.keyboards.kb_parent import ikb_parent_children
from bot.cbdata import GenderCFactory
from db_service.service import valid_number
from db_service.dbservice import ChildDB, ParentDB


router = Router()


@router.callback_query(Text('cb_add_one_more_parent'))
async def cb_add_one_more_parent(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Первый пункт опросника по добавлению еще одного родителя"""
    await callback.message.answer(text="Введите имя еще одного родителя")
    await state.set_state(AddOneMoreParentSGroup.parent_name)


@router.message(AddOneMoreParentSGroup.parent_name)
async def cb_add_one_more_parent_name(message: types.Message, state: FSMContext) -> None:
    """Добавление данных родителя - 2 этап имя родителя"""
    await state.update_data(name=message.text)
    await message.answer(f'Выберите пол - {message.text}', reply_markup=ikb_gender())
    await state.set_state(AddOneMoreParentSGroup.gender)


@router.callback_query(GenderCFactory.filter(), AddOneMoreParentSGroup.gender)
async def cb_add_one_more_parent_gender(callback: types.CallbackQuery,
                               callback_data: GenderCFactory,
                               state: FSMContext) -> None:
    """Добавление данных родителя - 3 этап пол родителя"""
    await state.update_data(gender=int(callback_data.gender)) # Standard ISO/IEC 5218 0 - not known, 1 - Male, 2 - Female, 9 - Not applicable
    data = await state.get_data()  # Загружаем данные из FSM
    await callback.message.answer(f'Введите номер телефона <b>{data["name"]}</b>:')
    await state.set_state(AddOneMoreParentSGroup.parent_number)


@router.message(AddOneMoreParentSGroup.parent_number)
async def cb_add_one_more_parent_phone(message: types.Message, state: FSMContext) -> None:
    """Добавление данных родителя - 4 этап номер телефона родителя"""
    parent_number = valid_number(message.text)
    if parent_number:
        parent_data = ParentDB.is_bot_user_id(int(message.from_user.id)) # Получем его данные
        all_children_id = ChildDB.get_all_children_id(parent_id=parent_data['id'])
        await state.update_data(phone=parent_number)
        await state.update_data(all_children_id=all_children_id)
        data = await state.get_data()
        ParentDB.add_one_more_parent(data=data)
        await message.answer(f'Родитель добавлен', reply_markup=ikb_parent_children(bot_user_id=message.from_user.id))
    else:
        await message.reply(f'Номер - "{message.text}" не распознан\nПожалуйста введите номер телефон в формате 7 987 654 32 10')

