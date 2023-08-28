"""Опросник для добавления еще одного ребенка"""
import sys

from aiogram import Router, types
from aiogram.filters.text import Text
from aiogram.fsm.context import FSMContext


sys.path.append("..")
from bot.statesgroup import AddOneMoreChildStatesGroup  # noqa: E402
from bot.keyboards.kb_general import ikb_gender  # noqa: E402
from bot.keyboards.kb_parent import ikb_parent_children  # noqa: E402
from bot.cbdata import GenderCFactory  # noqa: E402
from db_service.service import valid_number  # noqa: E402
from db_service.dbservice import ChildDB, ParentDB  # noqa: E402
from db_service.pydantic_model import Child_Base  # noqa: E402


router = Router()


@router.callback_query(Text('cb_add_child'))
async def cb_add_one_more_child(
        callback: types.CallbackQuery, state: FSMContext) -> None:
    """Первый пункт опросника по добавлению еще одного ребенка"""
    await callback.message.answer(text="Введите имя еще одного ребенка")
    await state.set_state(AddOneMoreChildStatesGroup.name)


@router.message(AddOneMoreChildStatesGroup.name)
async def cb_add_one_more_child_name(
        message: types.Message, state: FSMContext) -> None:
    """Добавление данных ребенка - 2 этап имя ребенка"""
    await state.update_data(name=message.text)
    await message.answer(
        text=f'Выберите пол - {message.text}',
        reply_markup=ikb_gender())

    await state.set_state(AddOneMoreChildStatesGroup.gender)


@router.callback_query(
        GenderCFactory.filter(),
        AddOneMoreChildStatesGroup.gender)
async def cb_add_one_more_child_gender(
        callback: types.CallbackQuery,
        callback_data: GenderCFactory,
        state: FSMContext) -> None:
    """Добавление данных ребенка - 3 этап пол ребенка"""
    # Standard ISO/IEC 5218 0 -not known, 1 -Male, 2 -Female, 9 -Not applicable
    await state.update_data(sex=int(callback_data.gender))
    data = await state.get_data()
    await callback.message.answer(
        text=f'Введите номер телефона <b>{data["name"]}</b>:')
    await state.set_state(AddOneMoreChildStatesGroup.phone)


@router.message(AddOneMoreChildStatesGroup.phone)
async def cb_add_one_more_child_phone(
        message: types.Message, state: FSMContext) -> None:
    """Добавление данных ребенка - 4 этап номер телефона ребенка"""
    parent_number = valid_number(message.text)

    if parent_number:
        first_add_child_id = ChildDB.get_first_child_id(
            bot_user_id=int(message.from_user.id))

        all_parent_id = ParentDB.get_all_parent_id(child_id=first_add_child_id)

        await state.update_data(phone=parent_number)
        state_data = await state.get_data()

        data = Child_Base.validate(state_data)
        child = ChildDB.add_child(data=data, all_parent_id=all_parent_id)
        await message.answer(
            text=f'Рeбенок добавлен\n{child}',
            reply_markup=ikb_parent_children(bot_user_id=message.from_user.id))
        await state.clear()
    else:
        await message.reply(
            text=f'Номер - "{message.text}" не распознан\n'
            f'Пожалуйста введите номер телефон в формате 7 987 654 32 10')
