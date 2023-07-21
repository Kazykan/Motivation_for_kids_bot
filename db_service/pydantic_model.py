from pydantic import BaseModel
from typing import List
from datetime import datetime, date


class Week_list(BaseModel):
    week_id: int
    week: str

class Parent_and_child(BaseModel):
    name: str
    bot_user_id: int
    phone_number: str
    sex: int
    child_number: str
    child_name: str
    child_sex: int


class Child_Base(BaseModel):
    name: str
    phone: str
    sex: int


class Children_in_parent_base(BaseModel):
    id: int
    name: str
    phone: str
    sex: int



class Parent_list(BaseModel):
    id: int
    name: str


class Parent_base(BaseModel):
    name: str
    bot_user_id: int
    phone: str
    sex: int
    access: int


class Parent_base_and_child(Parent_base):
    children: List[Children_in_parent_base]


class Activity_base(BaseModel):
    name: str
    title: str | None
    percent_complete: int
    cost: int
    max_cost: int | None
    child_id: int


class Activity_list(BaseModel):
    id: int
    name: str
    title: str
    percent_complete: int
    cost: int
    max_cost: int


class Child_serialize_activities(Child_Base):
    id: int
    bot_user_id: int | None
    birthday: date | None
    max_payout: int | None
    phone: str | None
    parents: List[Parent_list]
    activities: List[Activity_list]


class Activity_day_Base(BaseModel):
    is_done: bool | None
    day: date | None


class Activity_days_list(Activity_day_Base):
    id: int


class Activity_day_serializer(Activity_days_list):
    activity_id: int


class Activity_serialize(Activity_base):
    id: int
    weeks: List[Week_list] | None
    activity_days: List[Activity_days_list] | None