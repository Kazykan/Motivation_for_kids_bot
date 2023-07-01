from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter


def ikb_start() -> types.InlineKeyboardMarkup:
    """Кнопки первые: выбор родитель или ребенок"""
    ikb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text='Родитель 🇬🇧', callback_data='cb_parent')],
        [types.InlineKeyboardButton(text='Ребенок 🗓', callback_data='cb_child')],
        [types.InlineKeyboardButton('Ссылка на видео про мотивацию', url='https://www.youtube.com/watch?v=6x6B0bmtmjI')],
    ], markup=types.ReplyKeyboardRemove())
    return ikb



async def cmd_start(message: types.Message, state: FSMContext):
    # TODO: Добавить проверку есть ли такой bot_user_id в БД
    await state.finish()
    # Удаляем кнопки внизу
    await message.answer('Добро пожаловать!\n', reply_markup=types.ReplyKeyboardRemove())
    # Добавляем кнопки 
    await message.answer(
        'В телеграмм бот Мотивация!\nВыберите кто вы?',
        reply_markup=ikb_start()
    )


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())



def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")
    dp.register_message_handler(cmd_cancel, Text(equals="отмена", ignore_case=True), state="*")