from datetime import date
from typing import Optional
from aiogram.filters.callback_data import CallbackData


class BaseChildCFactory(CallbackData, prefix="cb_child"):
    """Префикс — это общая подстрока в начале, по которой фреймворк будет определять, какая структура лежит в колбэке"""
    id: int
    day: str | bool


class ChildInfoCFactory(CallbackData, prefix="cb_child_info"):
    id: int
    day: str | bool


class ActivityDayCompletionNotificationCFactory(CallbackData, prefix="cb_activity_day_completion"):
    child_id: int
    activity_day_id: int


class ActivityCFactory(CallbackData, prefix='cb_activity'):
    activity_id: int
    tick: str


class ActivityChildCFactory(CallbackData, prefix='cb_activity_child'):
    activity_id: int


class TickChangeActivityCFactory(CallbackData, prefix='cb_activity_edit'):
    activity_day_id: int


class DeleteActivityCFactory(CallbackData, prefix='cb_activity_delete'):
    activity_id: int


class AddActivityCFactory(CallbackData, prefix='cb_add_activity'):
    child_id: int


class ChangeOneWeekOnActivityCFactory(CallbackData, prefix='cb_week_activity'):
    week_id: int
    activity_id: int
    edit: bool


class GenderCFactory(CallbackData, prefix='cb_gender'):
    gender: int