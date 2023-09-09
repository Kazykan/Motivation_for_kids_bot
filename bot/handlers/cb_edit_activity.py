"""Изменение задания"""
import sys

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

sys.path.append("..")
from bot.keyboards.ikb_activity_edit_list import \
    ikb_activity_edit_list  # noqa: E402
from bot.keyboards.ikb_child_menu import ikb_child_menu  # noqa: E402
from bot.cbdata import EditActivityCFactory, \
    EditActivityOptionsCFactory  # noqa: E402
from bot.statesgroup import EditActivitySGroup  # noqa: E402
from db_service.dbservice import ActivityDB  # noqa: E402
from db_service.pydantic_model import Activity_serialize  # noqa: E402


router = Router()


@router.callback_query(EditActivityCFactory.filter())
async def cb_edit_activity(
        callback: types.CallbackQuery,
        callback_data: EditActivityCFactory) -> None:
    """Изменения активности"""
    activity = Activity_serialize.validate(
        ActivityDB.get_info(activity_id=callback_data.activity_id))
    await callback.message.edit_text(
        text=f'Изменить данные по задаче <b> {activity.name} </b>'
        f'\nВыберите что изменить',
        reply_markup=ikb_activity_edit_list(
            activity_id=callback_data.activity_id)
    )


@router.callback_query(EditActivityOptionsCFactory.filter())
async def cb_edit_activity_option(
        callback: types.CallbackQuery,
        state: FSMContext,
        callback_data: EditActivityOptionsCFactory) -> None:
    """Изменения полей активности"""
    activity = Activity_serialize.validate(
        ActivityDB.get_info(activity_id=callback_data.activity_id))

    await state.update_data(activity_id=callback_data.activity_id)
    await state.update_data(child_id=activity.child_id)

    if callback_data.field == 'name':
        text = f'{activity.name}'

        await callback.message.edit_text(
            text=f'Изменить данные по задаче <b> {activity.name} </b>\n'
            f'старое(ая) {callback_data.description} - {text}\n'
            f'Введите {callback_data.description} ниже'
        )
        await state.update_data(update_field=f'{callback_data.field}')
        # await state.set_state(EditActivityStatesGroup.name)

    elif callback_data.field == 'title':
        text = f'{activity.title}'

        await callback.message.edit_text(
            text=f'Изменить данные по задаче <b> {activity.name} </b>\n'
            f'старое(ая) {callback_data.description} - {text}\n'
            f'Введите {callback_data.description} ниже'
        )
        await state.update_data(update_field=f'{callback_data.field}')
        # await state.set_state(EditActivityStatesGroup.title)

    elif callback_data.field == 'percent_complete':
        text = f'{activity.percent_complete}'

        await callback.message.edit_text(
            text=f'Изменить данные по задаче <b> {activity.name} </b>\n'
            f'старое(ая) {callback_data.description} - {text}\n'
            f'Введите {callback_data.description} ниже'
        )
        await state.update_data(update_field=f'{callback_data.field}')
        # await state.set_state(EditActivityStatesGroup.percent_complete)

    elif callback_data.field == 'cost':
        text = f'{activity.cost}'

        await callback.message.edit_text(
            text=f'Изменить данные по задаче <b> {activity.name} </b>\n'
            f'старое(ая) {callback_data.description} - {text}\n'
            f'Введите {callback_data.description} ниже'
        )
        await state.update_data(update_field=f'{callback_data.field}')
        # await state.set_state(EditActivityStatesGroup.cost)
    await state.set_state(EditActivitySGroup.next)


@router.message(EditActivitySGroup.next)
async def edit_activity_option_next(
        message: types.Message, state: FSMContext) -> None:
    """Изменения полей активности - 2 этап добавление в БД изменений"""
    data = await state.get_data()  # Загружаем данные из FSM
    await message.answer(text=f'{data}')
    if data['update_field'] == 'name':
        print('name')
        ActivityDB.update_info(
            activity_id=int(data["activity_id"]),
            name=message.text)

    if data['update_field'] == 'title':
        print('Update title')
        ActivityDB.update_info(
            activity_id=int(data["activity_id"]),
            title=message.text)

    if data['update_field'] == 'percent_complete':
        print('percent')
        try:
            if 0 >= int(message.text) < 100:
                raise ValueError
            ActivityDB.update_info(
                activity_id=int(data["activity_id"]),
                percent_complete=int(message.text))
        except ValueError:
            await message.edit_text(
                text="от 1 до 100 % вводите только цифры!")
            await state.set_state(EditActivitySGroup.next)

    if data['update_field'] == 'cost':
        print('cost update')
        try:
            if 0 >= int(message.text) < 100000:
                raise ValueError
            ActivityDB.update_info(
                activity_id=int(data["activity_id"]),
                cost=int(message.text))
        except ValueError:
            await message.edit_text(
                "от 1 до 100 000 ₽ вводите только цифры!")
            await state.set_state(EditActivitySGroup.next)
    await message.answer(
        text='Данные обновлены',
        reply_markup=ikb_child_menu(child_id=data['child_id']))


# @router.message(AddActivityStatesGroup.percent_complete)
# async def child_add_activity_percent_complete(
#         message: types.Message, state: FSMContext) -> None:
#     """Добавить задание для ребенка - 4 этап стоимость выполнения"""
#     data = await state.get_data()
#     try:
#         if 0 >= int(message.text) < 100:
#             raise ValueError
#         await state.update_data(percent_complete=int(message.text))
#     except ValueError:
#         await message.edit_text(
#             f"от 1 до 100 % вводите только цифры!"
#             f"Введите процент выполнения для задания - {data['name']}"
#             )
#         await state.set_state(AddActivityStatesGroup.percent_complete)
#     await message.answer(f"Введите стоимость для задания: {data['name']}")
#     await state.set_state(AddActivityStatesGroup.cost)


# @router.message(AddActivityStatesGroup.cost)
# async def child_add_activity_cost(
#         message: types.Message, state: FSMContext) -> None:
#     """Добавить задание для ребенка - 5 этап выбор дней недели"""
#     data = await state.get_data()
#     try:
#         if 0 >= int(message.text) < 100000:
#             raise ValueError
#         await state.update_data(cost=int(message.text))
#         await state.update_data(max_cost=int(message.text))
#     except ValueError:
#         await message.edit_text(
#             f"от 1 до 100 000 ₽ вводите только цифры!"
#             f"Введите стоимость для задания: {data['name']}"
#             )
#         await state.set_state(AddActivityStatesGroup.cost)
#     data = await state.get_data()  # получаем новые данные в state
#     try:
#         info = Activity_base.validate(data)
#         # Создаем Активность и получаем ее данные
#         activity = Activity_serialize.validate(ActivityDB.add(info))
#         await message.answer(
#             f"<code>{activity_to_text(activity)}</code>"
#             f"Выберите дни недели для задания"
#             f"<b> ВНИМАНИЕ !!! </b> "
#             f"Изменения приведут к обнулению отметок в текущей неделе",
#             reply_markup=ikb_weeks(activity_id=activity.id)
#             )
#         await state.clear()
#     except ValueError as e:
#         await message.edit_text(f'{e}')


# @router.callback_query(ChangeOneWeekOnActivityCFactory.filter())
# async def cb_change_week_on_activity(
#         callback: types.CallbackQuery,
#         callback_data: ChangeOneWeekOnActivityCFactory
#         ) -> None:
#     """Проверяем есть в задаче этот день недели если нет добавляем"""
#     if callback_data.edit:
#         try:
#             # Проверка есть ли запись в БД
#             week = get_activity_week(
#                 activity_id=callback_data.activity_id,
#                 week_id=callback_data.week_id
#                 )
#             if week:  # Если есть удаляем
#                 delete_activity_week(
#                     activity_id=callback_data.activity_id,
#                     week_id=callback_data.week_id
#                     )
#             else:  # Если нет добавляем
#                 add_activity_week(
#                     activity_id=callback_data.activity_id,
#                     week_id=callback_data.week_id
#                     )
#         except ValueError as e:
#             await callback.message.answer(f'{e}')
#     activity = Activity_serialize.validate(
#         ChildDB.get_activity_one(activity_id=int(callback_data.activity_id)))
#     info = activity_to_text(activity)
#     await callback.message.edit_text(
#         text=f'<code>{info}</code>\nВыберите дни недели для задания\n'
#              f'<b> ВНИМАНИЕ !!! </b> '
#              f'Изменения приведут к обнулению отметок в текущей неделе',
#              reply_markup=ikb_weeks(callback_data.activity_id)
#         )


# @router.callback_query(DeleteActivityCFactory.filter())
# async def cb_delete_activity(
#         callback: types.CallbackQuery,
#         callback_data: DeleteActivityCFactory) -> None:
#     """Удаление задания"""
#     info = ActivityDB.get_info(activity_id=callback_data.activity_id)
#     # Если есть подтверждение то удаляем
#     if callback_data.second_stage == 'yes':
#         ActivityDB.delete_activity(activity_id=callback_data.activity_id)
#         await callback.message.edit_text(
#             text=f'{info["name"]} - удален.',
#             reply_markup=ikb_list_of_activity(child_id=int(info["child_id"]))
#             )
#     else:
#         await callback.message.edit_text(
#             text=f'Подтвердите удаление задания -  {info["name"]} '
#             f'\n ВНИМАНИЕ !!! ',
#             reply_markup=ikb_delete_activity(
#                 activity_id=int(callback_data.activity_id),
#                 child_id=int(info["child_id"])
#             )
#         )
