"""Работа с ребенком и его заданиями"""
import sys

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text

sys.path.append("..")
from db_service.service import report_table_child
from db_service.dbservice import child_data
from db_service.pydantic_model import Child_serialize_activities, Parent_and_child, Parent_base_and_child, Children_in_parent_base


async def cb_child_info(callback: types.CallbackQuery) -> None:
    """Список заданий ребенка с возможностью удалить или добавить задания"""
    await callback.message.delete()
    child_id = callback.data[9:] # получаем только цифры от callback - cb_child_**
    # TODO: Добавить проверку доступа родителя к этому ребенку
    child_info = Child_serialize_activities.model_validate(child_data(child_id=child_id))
    info = report_table_child(child_info)
    await callback.message.answer(text=f'<code>{info}\n</code>', parse_mode="html")


def register_cb_handlers_child_activity(dp: Dispatcher):
    dp.register_callback_query_handler(cb_child_info,
                                       Text(startswith='cb_child_'),
                                       state='*')