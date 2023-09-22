"""Машина состояний для работы опросника"""
from aiogram.fsm.state import StatesGroup, State


class AddParentStatesGroup(StatesGroup):
    """Добавление Родителя и детей"""
    parent_number = State()
    gender = State()
    child_phone = State()
    child_name = State()
    child_gender = State()


class AddOneMoreParentSGroup(StatesGroup):
    """Добавление еще одного Родителя"""
    parent_name = State()
    gender = State()
    parent_number = State()


class AddOneMoreChildSGroup(StatesGroup):
    """Добавление еще одного Ребенка"""
    phone = State()
    name = State()
    gender = State()


class AddActivitySGroup(StatesGroup):
    """Добавление задания"""
    name = State()
    title = State()
    percent_complete = State()
    cost = State()
    weeks = State()


class EditActivitySGroup(StatesGroup):
    """Редактированию задания"""
    next = State()


class AddChildStatesGroup(StatesGroup):
    """Машина состояний для работы опросника по регистрации Ребенка"""
    child_phone = State()
