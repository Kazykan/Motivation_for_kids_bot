from aiogram.fsm.state import StatesGroup, State


class AddParentStatesGroup(StatesGroup):
    """Машина состояний для работы опросника по добавлению Родителя и детей"""
    parent_number = State()
    gender = State()
    child_phone = State()
    child_name = State()
    child_gender = State()


class AddOneMoreParentSGroup(StatesGroup):
    """Машина состояний для работы опросника по добавлению еще одного Родителя"""
    parent_name = State()
    gender = State()
    parent_number = State()


class AddOneMoreChildStatesGroup(StatesGroup):
    """Машина состояний для работы опросника по добавлению еще одного Родителя"""
    phone = State()
    name = State()
    gender = State()


class AddActivityStatesGroup(StatesGroup):
    """Машина состояний для работы опросника по добавлению задания"""
    name = State()
    title = State()
    percent_complete = State()
    cost = State()
    weeks = State()


class EditActivityStatesGroup(StatesGroup):
    """Машина состояний для работы опросника по редактированию задания"""
    next = State()
    # name = State()
    # title = State()
    # percent_complete = State()
    # cost = State()
