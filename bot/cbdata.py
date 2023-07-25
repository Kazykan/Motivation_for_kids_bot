from datetime import date
from typing import Optional
from aiogram.filters.callback_data import CallbackData


class ChildCallbackFactory(CallbackData, prefix="cb_child"):
    """Префикс — это общая подстрока в начале, по которой фреймворк будет определять, какая структура лежит в колбэке"""
    id: int
    day: str | bool



class ActivityCallbackFactory(CallbackData, prefix='cb_activity'):
    activity_id: int
    tick: str


class ActivityChildCallbackFactory(CallbackData, prefix='cb_activity_child'):
    activity_id: int


class TickChangeActivityCallbackFactory(CallbackData, prefix='cb_activity_edit'):
    activity_day_id: int


class DeleteActivityCallbackFactory(CallbackData, prefix='cb_activity_delete'):
    activity_id: int


class AddActivityCallbackFactory(CallbackData, prefix='cb_add_activity'):
    child_id: int


class ChangeOneWeekOnActivityCallbackFactory(CallbackData, prefix='cb_week_activity'):
    week_id: int
    activity_id: int
    edit: bool


class GenderCallbackFactory(CallbackData, prefix='cb_gender'):
    gender: int