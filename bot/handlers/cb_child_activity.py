"""Работа с ребенком и его заданиями"""
import sys

from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder


sys.path.append("..")
from bot.statesgroup import AddActivityStatesGroup
from bot.cbdata import ActivityCallbackFactory, AddActivityCallbackFactory, ChildCallbackFactory, DeleteActivityCallbackFactory, TickChangeActivityCallbackFactory, ChangeOneWeekOnActivityCallbackFactory
from db_service.dbservice import add_activity_week, change_activity_day_is_done, delete_activity_week, get_activity_day, get_activity_week, get_child_activity_one
from db_service.pydantic_model import Activity_day_serializer, Activity_serialize, Child_serialize_activities, Activity_base
from db_service.service import activity_to_text, is_weekday_on, get_child_gender_emoji
from db_service.dbservice import add_activity, get_child_data, get_weeks_list_for_activities, report_table_child


router = Router()


def ikb_child_menu(child_id: int):
    """Кнопки список заданий ребенка (отметить, выбрать дни недели, удалить)
    + кнопка добавить еще задание"""
    child_info = Child_serialize_activities.validate(get_child_data(child_id=child_id))
    builder = InlineKeyboardBuilder()
    row = []
    for activity in child_info.activities:
        builder.button(text=f'{activity.name}',
                        callback_data=ActivityCallbackFactory(
                        activity_id=activity.id, tick='no'))
        builder.button(text=f'✔️📝',
                        callback_data=ActivityCallbackFactory(
                        activity_id=activity.id, tick='yes'))
        builder.button(text=f'🛠️📅',
            callback_data=ChangeOneWeekOnActivityCallbackFactory(
            week_id=1, activity_id=activity.id, edit=False))
        builder.button(text=f'🗑',
                        callback_data=DeleteActivityCallbackFactory(activity_id=activity.id))
        row.append(4)
    row.append(2)
    builder.button(text='➕ Добавить задание',
                    callback_data=AddActivityCallbackFactory(child_id=child_info.id))
    builder.button(text='🔙 Назад', callback_data="cb_parent")
    builder.adjust(*row)
    return builder.as_markup()


def ikb_activity_tick(activity_id: int):
    """Одно задание по дням недели и возможность отметить выполнения по дням"""
    activity = Activity_serialize.validate(
        get_child_activity_one(activity_id=activity_id))
    builder = InlineKeyboardBuilder()
    days = sorted(activity.activity_days, key=lambda x: x.day)  # Сортировка по дате
    for day in days:
        if day.is_done:
            is_done = '✅'
        else: is_done = '❌'
        builder.button(text=f'{day.day.strftime("%a %d %b")} {is_done}',
                       callback_data='cb_activity_day_one')
        builder.button(text=f'изменить 🔄',
            callback_data=TickChangeActivityCallbackFactory(activity_day_id=day.id))
    builder.button(text='Перейти списку заданий', callback_data=ChildCallbackFactory(id=activity.child_id))
    builder.adjust(2)
    return builder.as_markup()


def ikb_weeks(activity_id: int) -> types.InlineKeyboardMarkup:
    """Кнопки дни недели"""
    activity_info = Activity_serialize.validate(get_weeks_list_for_activities(activity_id))
    builder = InlineKeyboardBuilder()
    for week_id, value in is_weekday_on(activity_info.weeks).items():
        builder.button(text=f'{value}',
            callback_data=ChangeOneWeekOnActivityCallbackFactory(
            week_id=week_id, activity_id=activity_id, edit=True))
    builder.button(text='Перейти списку заданий', callback_data=ChildCallbackFactory(id=activity_info.child_id))
    builder.adjust(7)
    return builder.as_markup()


@router.callback_query(TickChangeActivityCallbackFactory.filter())
async def cb_tick_change_activity_fab(callback: types.CallbackQuery,
                    callback_data: TickChangeActivityCallbackFactory
                    ) -> None:
    """ Изменения статуса выполнения задания по дням"""
    try:
        change_activity_day_is_done(activity_day_id=int(callback_data.activity_day_id))
        # TODO: Убрать лишний запрос снизу
        activity_day = Activity_day_serializer.validate(
            get_activity_day(activity_day_id=callback_data.activity_day_id))
        activity = Activity_serialize.validate(
        get_child_activity_one(activity_id=int(activity_day.activity_id)))
        info = activity_to_text(activity)
        await callback.message.edit_text(text=f'<code>{info}\n</code>',
                                        reply_markup=ikb_activity_tick(activity.id))
    except:
        await callback.message.answer('Ошибка ввода')


@router.callback_query(ActivityCallbackFactory.filter())
async def cb_child_activity_fab(callback: types.CallbackQuery,
                                callback_data: ActivityCallbackFactory) -> None:
    """Подробности про задание + отметка о выполнении"""
    # TODO: Убрать повторение функции 3 строчки вниз
    activity = Activity_serialize.validate(
        get_child_activity_one(activity_id=int(callback_data.activity_id)))
    info = activity_to_text(activity)
    if callback_data.tick == 'no':
        await callback.message.edit_text(text=f'<code>{info}\n</code>',
                                        reply_markup=ikb_child_menu(child_id=activity.child_id))
    else:
        await callback.message.edit_text(text=f'<code>{info}\n</code>',
                                        reply_markup=ikb_activity_tick(activity.id))


@router.callback_query(ChildCallbackFactory.filter())
async def cb_child_info_fab(callback: types.CallbackQuery,
                            callback_data: ChildCallbackFactory) -> None:
    """Список заданий ребенка с возможностью удалить или добавить задания"""
    # TODO: Добавить проверку доступа родителя к этому ребенку
    child_info = Child_serialize_activities.validate(get_child_data(child_id=callback_data.id))
    info = report_table_child(child_info)
    await callback.message.edit_text(text=f'<code>{info}\n</code>\n'
        f'Список заданий {get_child_gender_emoji(child_info.sex)} {child_info.name}',
        reply_markup=ikb_child_menu(child_id=int(callback_data.id)))


@router.callback_query(AddActivityCallbackFactory.filter())
async def cb_child_add_activity(callback: types.CallbackQuery,
                                state: FSMContext,
                                callback_data: AddActivityCallbackFactory) -> None:
    """Добавить задание для ребенка"""
    child_info = Child_serialize_activities.validate(
        get_child_data(child_id=callback_data.child_id))
    # TODO: Добавить проверку доступа родителя к этому ребенку
    await callback.message.edit_text(f'Добавить задание для: {get_child_gender_emoji(child_info.sex)} {child_info.name}\n'
                                  f'Введите название задания, желательно состоящее из одного слова...\n')
    await state.update_data(child_id=child_info.id)
    await state.set_state(AddActivityStatesGroup.name)


@router.message(AddActivityStatesGroup.name)
async def child_add_activity_name(message: types.Message, state: FSMContext) -> None:
    """Добавить задание для ребенка - 2 этап описание задания"""
    await state.update_data(name=message.text)
    data = await state.get_data()  # Загружаем данные из FSM
    await message.answer(f"Введите описание для задания: <b>{data['name']}</b>")
    await state.set_state(AddActivityStatesGroup.title)


@router.message(AddActivityStatesGroup.title)
async def child_add_activity_title(message: types.Message, state: FSMContext) -> None:
    """Добавить задание для ребенка - 3 этап процент для выполнения"""
    await state.update_data(title=message.text)
    data = await state.get_data()  # Загружаем данные из FSM
    await message.answer(f"Введите процент выполнения для задания - <b>{data['name']}</b>"
                         f"\nот 1 до 100 % вводите только цифры")
    await state.set_state(AddActivityStatesGroup.percent_complete)


@router.message(AddActivityStatesGroup.percent_complete)
async def child_add_activity_percent_complete(message: types.Message, state: FSMContext) -> None:
    """Добавить задание для ребенка - 4 этап стоимость выполнения"""
    data = await state.get_data()
    try:
        if 0 >= int(message.text) < 100:
            raise ValueError
        await state.update_data(percent_complete=int(message.text))
    except ValueError:
        await message.edit_text(f"от 1 до 100 % вводите только цифры!"
            f"Введите процент выполнения для задания - {data['name']}")
        await state.set_state(AddActivityStatesGroup.percent_complete)
    await message.answer(f"Введите стоимость для задания: {data['name']}")
    await state.set_state(AddActivityStatesGroup.cost)


@router.message(AddActivityStatesGroup.cost)
async def child_add_activity_cost(message: types.Message, state: FSMContext) -> None:
    """Добавить задание для ребенка - 5 этап выбор дней недели"""
    data = await state.get_data()
    try:
        if 0 >= int(message.text) < 100000:
            raise ValueError
        await state.update_data(cost=int(message.text))
        await state.update_data(max_cost=int(message.text))
    except ValueError:
        await message.edit_text(f"от 1 до 100 000 ₽ вводите только цифры!"
            f"Введите стоимость для задания: {data['name']}")
        await state.set_state(AddActivityStatesGroup.cost)
    data = await state.get_data()  # получаем новые данные в state
    try:
        info = Activity_base.validate(data)
        activity = Activity_serialize.validate(add_activity(info))  # Создаем Активность и получаем ее данные
        await message.answer(f"<code>{activity_to_text(activity)}</code>"
            f"Выберите дни недели для задания"
            f"<b> ВНИМАНИЕ !!! </b> Изменения приведут к обнулению отметок в текущей неделе",
            reply_markup=ikb_weeks(activity_id=activity.id))
        await state.clear()
    except ValueError as e:
        await message.edit_text(f'{e}')


@router.callback_query(ChangeOneWeekOnActivityCallbackFactory.filter())
async def cb_change_week_on_activity(callback: types.CallbackQuery,
                                  callback_data: ChangeOneWeekOnActivityCallbackFactory) -> None:
    """Проверяем есть в задаче этот день недели если нет добавляем"""
    if callback_data.edit:
        try:
            week = get_activity_week(activity_id=callback_data.activity_id,
                            week_id=callback_data.week_id)  # Проверка есть ли запись в БД
            if week: # Если есть удаляем
                delete_activity_week(activity_id=callback_data.activity_id,
                        week_id=callback_data.week_id)
            else: # Если нет добавляем
                add_activity_week(activity_id=callback_data.activity_id,
                        week_id=callback_data.week_id)
        except ValueError as e:
            await callback.message.answer(f'{e}')
    activity = Activity_serialize.validate(
        get_child_activity_one(activity_id=int(callback_data.activity_id)))
    info = activity_to_text(activity)
    await callback.message.edit_text(
        text=f'<code>{info}</code>\nВыберите дни недели для задания\n'
            f'<b> ВНИМАНИЕ !!! </b> Изменения приведут к обнулению отметок в текущей неделе',
            reply_markup=ikb_weeks(callback_data.activity_id)
        )
