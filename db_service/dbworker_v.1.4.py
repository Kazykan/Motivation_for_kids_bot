import datetime

from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Date, Text,\
    Boolean, Table, ForeignKey, SmallInteger
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase, Mapped,\
    mapped_column
from sqlalchemy.ext.declarative import declarative_base
# from config import DATABASE


DATABASE = "sqlite:///sqlite.db"
engine = create_engine(DATABASE, echo=True)  #TODO: написать доступ к БД

Base = declarative_base()

#  Связь многие-ко-многим дети - родители
child_mtm_parent = Table(
    'child_mtm_parent',
    Base.metadata,
    Column('child_id', ForeignKey('child.id')),
    Column('parent_id', ForeignKey('parent.id'))
)


activity_mtm_week = Table(
    'activity_mtm_week',
    Base.metadata,
    Column('activity_id', ForeignKey('activity.id')),
    Column('week_id', ForeignKey('week.id'))
)


class Child(Base):
    """Ребенок"""
    __tablename__ = 'child'

    id = Column(primary_key=True)
    name = Column(String(30))
    birthday = Column(Date)
    sex = Column(SmallInteger)  # Standard ISO/IEC 5218 0 - not known, 1 - Male, 2 - Female, 9 - Not applicable
    max_payout = Column(Integer)
    parents = relationship(
        secondary=child_mtm_parent,
        back_populates="children"
        )
    activities = relationship()


class Parent(Base):
    """Родители"""
    __tablename__ = 'parent'

    id = Column(primary_key=True)
    name = Column(String(30))
    sex = Column(SmallInteger)  # Standard ISO/IEC 5218 0 - not known, 1 - Male, 2 - Female, 9 - Not applicable
    access = Column(Integer, default=0) #TODO расписать функционал доступа
    children = relationship(
        secondary=child_mtm_parent,
        back_populates="parents"
    )

    def __repr__(self) -> str:
        return f"Parent(id={self.id!r}, name={self.name!r}, sex={self.sex!r}, access={self.access!r})"
    

class Activity(Base):
    """Активности"""
    __tablename__ = 'activity'

    id = Column(primary_key=True)
    name = Column(String(50))
    percent_complete = Column(SmallInteger)  # Процент выполнения для завершения задания
    cost = Column(SmallInteger)  # стоимость выполнения задания
    child_id = Column(ForeignKey('child.id'))
    weeks = relationship(
        secondary=activity_mtm_week,
        back_populates="activities"
    ) # выбор дня недели мтм
    activity_days = relationship()



class Week(Base):
    """День недели для активностей"""
    __tablename__ = "week"

    id = Column(primary_key=True)
    week_day = Column(String(2))
    activities = relationship(
        secondary=activity_mtm_week,
        back_populates="weeks"
    )


class Activity_day(Base):
    """Активность по дням"""
    __tablename__ = "activity_day"

    id = Column(primary_key=True)
    is_done = Column(Boolean, default=False)
    day = Column(Date)
    Activity_id = Column(ForeignKey('activity.id'))


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()