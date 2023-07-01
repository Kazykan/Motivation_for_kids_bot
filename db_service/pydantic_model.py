from pydantic import BaseModel
from typing import List
from datetime import datetime, date


class Parent_and_child(BaseModel):
    name: str
    bot_user_id: int
    phone_number: str
    sex: int
    child_number: str
    child_name: str
    child_sex: int


class Children_in_parent_base(BaseModel):
     id: int
     name: str
     phone: str


class Parent_base(BaseModel):
    name: str
    bot_user_id: int
    phone: str
    sex: int
    access: int
    children: List[Children_in_parent_base]


