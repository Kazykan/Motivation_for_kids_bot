from aiogram import Router, types
from aiogram.filters import Command
from aiogram.filters.text import Text
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot.keyboards.for_start import ikb_start


router = Router()


@router.message(Command('cancel'))
@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()  # Clear FSM
    await message.answer('Добро пожаловать!\n', reply_markup=types.ReplyKeyboardRemove())
    await message.answer(
        "В телеграмм бот Мотивация!\nВыберите кто вы?",
        reply_markup=ikb_start()
    )