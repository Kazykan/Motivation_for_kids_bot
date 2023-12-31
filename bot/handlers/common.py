from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.handlers.cb_child import ikb_child_activity_list

from bot.keyboards.for_start import ikb_start
from bot.keyboards.kb_parent import ikb_parent_children
from db_service.dbservice import ChildDB, ParentDB, report_table_child


router = Router()


@router.message(Command('cancel'))
@router.message(Command('start'))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()  # Clear FSM
    parent_id = ParentDB.is_bot_user_id(
        bot_user_id=int(message.from_user.id)
        )  # Получем его данные
    child_id = ChildDB.is_bot_user_id(
        bot_user_id=int(message.from_user.id)
        )  # Получем его данные
    print(f'parent_id: {parent_id}\nchild_id: {child_id}')
    if parent_id is not None:
        # если родитель есть запускаем функцию работы с ним
        await message.answer(
            text='Выберите ребенка',
            reply_markup=ikb_parent_children(
                bot_user_id=int(message.from_user.id)
                )
            )
    elif child_id is not None:
        info = report_table_child(child_id=child_id)
        await message.answer(
            text=f'<code>{info}\n</code>\n',
            reply_markup=ikb_child_activity_list(child_id=child_id)
            )
    else:
        await message.answer(
            text='Добро пожаловать!\n',
            reply_markup=types.ReplyKeyboardRemove()
            )
        await message.answer(
            text="В телеграмм бот Мотивация!\nВыберите кто вы?",
            reply_markup=ikb_start()
        )
