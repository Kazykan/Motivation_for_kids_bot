"""Работа с ребенком и его заданиями"""
import sys

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.keyboards.ikb_activity_tick import ikb_activity_tick
from bot.keyboards.ikb_child_menu import ikb_child_menu
# from aiogram.types import FSInputFile


sys.path.append("..")
from bot.keyboards.kb_delete_activity import ikb_delete_activity  # noqa: E402
from bot.keyboards.kb_list_of_activity import ikb_list_of_activity  # noqa: E402
from bot.statesgroup import AddActivitySGroup  # noqa: E402
from bot.cbdata import ActivityCallbackFactory, AddActivityCFactory, \
    BaseChildCFactory, DeleteActivityCFactory, TickChangeActivityCFactory, \
    ChangeOneWeekOnActivityCFactory  # noqa: E402
from db_service.dbservice import ActivityDB, ActivityDayDB, ChildDB, \
    add_activity_week, delete_activity_week, report_table_child, \
    get_activity_day, get_activity_week  # noqa: E402
from db_service.pydantic_model import Activity_day_serializer, \
    Activity_serialize, Child_serialize_activities, Activity_base  # noqa: E402
from db_service.service import activity_to_text, convert_date, \
    is_weekday_on, get_child_gender_emoji  # noqa: E402
from db_service.dbservice import get_weeks_list_for_activities  # noqa: E402


router = Router()


def ikb_weeks(activity_id: int) -> types.InlineKeyboardMarkup:
    """Кнопки дни недели"""
    activity_info = Activity_serialize.validate(
        get_weeks_list_for_activities(activity_id)
        )
    builder = InlineKeyboardBuilder()
    for week_id, value in is_weekday_on(activity_info.weeks).items():
        builder.button(
            text=f'{value}',
            callback_data=ChangeOneWeekOnActivityCFactory(
                week_id=week_id,
                activity_id=activity_id,
                edit=True
                )
            )
    builder.button(
        text='Перейти списку заданий',
        callback_data=BaseChildCFactory(id=activity_info.child_id, day=False))
    builder.adjust(7)
    return builder.as_markup()


@router.callback_query(TickChangeActivityCFactory.filter())
async def cb_tick_change_activity_fab(
        callback: types.CallbackQuery,
        callback_data: TickChangeActivityCFactory) -> None:
    """Изменения статуса выполнения задания по дням"""
    try:
        ActivityDayDB.change_is_done(
            activity_day_id=int(callback_data.activity_day_id)
            )
        activity_day = Activity_day_serializer.validate(
            get_activity_day(activity_day_id=callback_data.activity_day_id))
        activity = Activity_serialize.validate(
            ChildDB.get_activity_one(activity_id=int(activity_day.activity_id))
            )
        info = activity_to_text(activity)
        await callback.message.edit_text(
            text=f'<code>{info}\n</code>',
            reply_markup=ikb_activity_tick(
                activity_id=activity.id,
                day=activity_day.day)
            )
    except:
        await callback.message.answer('Ошибка ввода')


@router.callback_query(ActivityCallbackFactory.filter())
async def cb_child_activity_fab(
        callback: types.CallbackQuery,
        callback_data: ActivityCallbackFactory) -> None:
    """Подробности про задание + отметка о выполнении"""
    # TODO: Убрать повторение функции 3 строчки вниз
    activity = Activity_serialize.validate(
        ChildDB.get_activity_one(activity_id=int(callback_data.activity_id)))
    info = activity_to_text(activity)
    if callback_data.tick == 'no':
        await callback.message.edit_text(
            text=f'<code>{info}\n</code>',
            reply_markup=ikb_child_menu(child_id=activity.child_id, day=False)
            )
    else:
        await callback.message.edit_text(
            text=f'<code>{info}\n</code>',
            reply_markup=ikb_activity_tick(
                activity_id=activity.id,
                day=convert_date(callback_data.day))
            )


@router.callback_query(BaseChildCFactory.filter())
async def cb_child_info_fab(callback: types.CallbackQuery,
                            callback_data: BaseChildCFactory) -> None:
    """Список заданий ребенка с возможностью удалить или добавить задания"""
    # TODO: Добавить проверку доступа родителя к этому ребенку
    child_info = Child_serialize_activities.validate(
        ChildDB.get_data(child_id=callback_data.id)
        )
    info = report_table_child(
        child_id=callback_data.id,
        day=convert_date(callback_data.day)
        )
    gender = get_child_gender_emoji(child_info.sex)
    await callback.message.edit_text(
        text=f'<code>{info}\n</code>\n'
        f'Список заданий {gender} {child_info.name}',
        reply_markup=ikb_child_menu(
            child_id=int(callback_data.id),
            day=callback_data.day)
            )
    # file_ids = []
    # image_from_pc = FSInputFile("1164470729.png")
    # result = await callback.message.answer_photo(
    #     image_from_pc,
    #     caption="Изображение из файла на компьютере"
    # )
    # file_ids.append(result.photo[-1].file_id)


@router.callback_query(AddActivityCFactory.filter())
async def cb_child_add_activity(callback: types.CallbackQuery,
                                state: FSMContext,
                                callback_data: AddActivityCFactory) -> None:
    """Добавить задание для ребенка"""
    child_info = Child_serialize_activities.validate(
        ChildDB.get_data(child_id=callback_data.child_id))
    # TODO: Добавить проверку доступа родителя к этому ребенку
    gender = get_child_gender_emoji(child_info.sex)
    await callback.message.edit_text(
        f'Добавить задание для: {gender} {child_info.name}\n'
        f'Введите название задания, желательно состоящее из одного слова...\n')
    await state.update_data(child_id=child_info.id)
    await state.set_state(AddActivitySGroup.name)


@router.message(AddActivitySGroup.name)
async def child_add_activity_name(
        message: types.Message, state: FSMContext) -> None:
    """Добавить задание для ребенка - 2 этап описание задания"""
    await state.update_data(name=message.text)
    data = await state.get_data()  # Загружаем данные из FSM
    await message.answer(
        text=f"Введите описание для задания: <b>{data['name']}</b>")
    await state.set_state(AddActivitySGroup.title)


@router.message(AddActivitySGroup.title)
async def child_add_activity_title(
        message: types.Message, state: FSMContext) -> None:
    """Добавить задание для ребенка - 3 этап процент для выполнения"""
    await state.update_data(title=message.text)
    data = await state.get_data()  # Загружаем данные из FSM
    await message.answer(
        f"Введите процент выполнения для задания - <b>{data['name']}</b>"
        f"\nот 1 до 100 % вводите только цифры"
        )
    await state.set_state(AddActivitySGroup.percent_complete)


@router.message(AddActivitySGroup.percent_complete)
async def child_add_activity_percent_complete(
        message: types.Message, state: FSMContext) -> None:
    """Добавить задание для ребенка - 4 этап стоимость выполнения"""
    data = await state.get_data()
    try:
        if 0 >= int(message.text) < 100:
            raise ValueError
        await state.update_data(percent_complete=int(message.text))
    except ValueError:
        await message.edit_text(
            f"от 1 до 100 % вводите только цифры!"
            f"Введите процент выполнения для задания - {data['name']}"
            )
        await state.set_state(AddActivitySGroup.percent_complete)
    await message.answer(f"Введите стоимость для задания: {data['name']}")
    await state.set_state(AddActivitySGroup.cost)


@router.message(AddActivitySGroup.cost)
async def child_add_activity_cost(
        message: types.Message, state: FSMContext) -> None:
    """Добавить задание для ребенка - 5 этап выбор дней недели"""
    data = await state.get_data()
    try:
        if 0 >= int(message.text) < 100000:
            raise ValueError
        await state.update_data(cost=int(message.text))
        await state.update_data(max_cost=int(message.text))
    except ValueError:
        await message.edit_text(
            f"от 1 до 100 000 ₽ вводите только цифры!"
            f"Введите стоимость для задания: {data['name']}"
            )
        await state.set_state(AddActivitySGroup.cost)
    data = await state.get_data()  # получаем новые данные в state
    try:
        info = Activity_base.validate(data)
        # Создаем Активность и получаем ее данные
        activity = Activity_serialize.validate(ActivityDB.add(info))
        await message.answer(
            f"<code>{activity_to_text(activity)}</code>"
            f"Выберите дни недели для задания"
            f"<b> ВНИМАНИЕ !!! </b> "
            f"Изменения приведут к обнулению отметок в текущей неделе",
            reply_markup=ikb_weeks(activity_id=activity.id)
            )
        await state.clear()
    except ValueError as e:
        await message.edit_text(f'{e}')


@router.callback_query(ChangeOneWeekOnActivityCFactory.filter())
async def cb_change_week_on_activity(
        callback: types.CallbackQuery,
        callback_data: ChangeOneWeekOnActivityCFactory
        ) -> None:
    """Проверяем есть в задаче этот день недели если нет добавляем"""
    if callback_data.edit:
        try:
            # Проверка есть ли запись в БД
            week = get_activity_week(
                activity_id=callback_data.activity_id,
                week_id=callback_data.week_id
                )
            if week:  # Если есть удаляем
                delete_activity_week(
                    activity_id=callback_data.activity_id,
                    week_id=callback_data.week_id
                    )
            else:  # Если нет добавляем
                add_activity_week(
                    activity_id=callback_data.activity_id,
                    week_id=callback_data.week_id
                    )
        except ValueError as e:
            await callback.message.answer(f'{e}')
    activity = Activity_serialize.validate(
        ChildDB.get_activity_one(activity_id=int(callback_data.activity_id)))
    info = activity_to_text(activity)
    await callback.message.edit_text(
        text=f'<code>{info}</code>\nВыберите дни недели для задания\n'
             f'<b> ВНИМАНИЕ !!! </b> '
             f'Изменения приведут к обнулению отметок в текущей неделе',
             reply_markup=ikb_weeks(callback_data.activity_id)
        )


@router.callback_query(DeleteActivityCFactory.filter())
async def cb_delete_activity(
        callback: types.CallbackQuery,
        callback_data: DeleteActivityCFactory) -> None:
    """Удаление задания"""
    info = ActivityDB.get_info(activity_id=callback_data.activity_id)
    # Если есть подтверждение то удаляем
    if callback_data.second_stage == 'yes':
        ActivityDB.delete_activity(activity_id=callback_data.activity_id)
        await callback.message.edit_text(
            text=f'{info["name"]} - удален.',
            reply_markup=ikb_list_of_activity(child_id=int(info["child_id"]))
            )
    else:
        await callback.message.edit_text(
            text=f'Подтвердите удаление задания -  {info["name"]} '
            f'\n ВНИМАНИЕ !!! ',
            reply_markup=ikb_delete_activity(
                activity_id=int(callback_data.activity_id),
                child_id=int(info["child_id"])
            )
        )
