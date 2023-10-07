import datetime

from typing import List
from sqlalchemy import create_engine, Column, Integer, String, \
    Boolean, Table, ForeignKey, SmallInteger
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase, \
    Mapped, mapped_column


DATABASE = "sqlite:///sqlite.db"
engine = create_engine(DATABASE, echo=True)  # TODO: написать доступ к БД


class Base(DeclarativeBase):
    pass


#  Связь многие-ко-многим дети - родители
child_mtm_parent = Table(
    'child_mtm_parent',
    Base.metadata,
    Column('child_id', ForeignKey('child.id')),
    Column('parent_id', ForeignKey('parent.id'))
)


#  Связь многие-ко-многим задачи - дни недели
activity_mtm_week = Table(
    'activity_mtm_week',
    Base.metadata,
    Column('activity_id', ForeignKey('activity.id')),
    Column('week_id', ForeignKey('week.id'))
)


class Child(Base):
    """Ребенок"""
    __tablename__ = 'child'

    id: Mapped[int] = mapped_column(primary_key=True)
    bot_user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(30))
    birthday: Mapped[datetime.date] = mapped_column(Date, nullable=True)
    # Standard ISO/IEC 5218 0 -not known, 1 -Male, 2 -Female, 9 -Not applicable
    sex: Mapped[int] = mapped_column(SmallInteger)
    max_payout: Mapped[int] = mapped_column(Integer, nullable=True)
    # TODO: Сделать уникальным поле
    phone: Mapped[str] = mapped_column(String(12))
    parents: Mapped[List["Parent"]] = relationship(
        secondary=child_mtm_parent,
        back_populates="children"
        )
    activities: Mapped[List["Activity"]] = relationship()

    @property
    def serialize(self):
        return {
            'id': self.id,
            'bot_user_id': self.bot_user_id,
            'name': self.name,
            'birthday': self.birthday,
            'sex': self.sex,
            'max_payout': self.max_payout,
            'phone': self.phone,
            'parents': [{'id': x.id, 'name': x.name} for x in self.parents],
            'activities': [
                {'id': x.id,
                 'name': x.name} for x in self.activities]
        }

    @property
    def serialize_activities(self):
        return {
            'id': self.id,
            'bot_user_id': self.bot_user_id,
            'name': self.name,
            'birthday': self.birthday,
            'sex': self.sex,
            'max_payout': self.max_payout,
            'phone': self.phone,
            'parents': [{'id': x.id, 'name': x.name} for x in self.parents],
            'activities': [{
                'id': x.id,
                'name': x.name,
                'title': x.title,
                'percent_complete': x.percent_complete,
                'cost': x.cost,
                'max_cost': x.max_cost,
                } for x in self.activities]
        }


class Parent(Base):
    """Родители"""
    __tablename__ = 'parent'

    id: Mapped[int] = mapped_column(primary_key=True)
    bot_user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(30))
    # Standard ISO/IEC 5218 0 -not known, 1 -Male, 2 -Female, 9 -Not applicable
    sex: Mapped[int] = mapped_column(SmallInteger)
    # TODO расписать функционал доступа
    access: Mapped[int] = mapped_column(Integer, default=0)
    phone: Mapped[str] = mapped_column(String(12))
    children: Mapped[List["Child"]] = relationship(
        secondary=child_mtm_parent,
        back_populates="parents"
    )

    @property
    def serialize(self):
        return {
            'id': self.id,
            'bot_user_id': self.bot_user_id,
            'name': self.name,
            'sex': self.sex,
            'access': self.access,
            'phone': self.phone,
            'children': [{'id': x.id,
                          'name': x.name,
                          'phone': x.phone,
                          'sex': x.sex} for x in self.children]
        }


class Activity(Base):
    """Активности"""
    __tablename__ = 'activity'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(15))
    title: Mapped[str] = mapped_column(String(200), nullable=True)
    # Процент выполнения для завершения задания
    percent_complete: Mapped[int] = mapped_column(SmallInteger)
    cost: Mapped[int] = mapped_column(SmallInteger)
    max_cost: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    child_id: Mapped[int] = mapped_column(ForeignKey('child.id'))
    weeks: Mapped[List["Week"]] = relationship(
        secondary=activity_mtm_week,
        back_populates="activities"
    )  # выбор дня недели мтм
    activity_days: Mapped[List["Activity_day"]] = relationship(
        cascade="all, delete, delete-orphan")

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'percent_complete': self.percent_complete,
            'cost': self.cost,
            'max_cost': self.max_cost,
            'child_id': self.child_id,
            'weeks': [
                {'week': x.week_day,
                 'week_id': x.id
                 } for x in self.weeks],
            'activity_days': [
                {'id': x.id,
                 'is_done': x.is_done,
                 'day': x.day
                 } for x in self.activity_days]
        }


class Week(Base):
    """День недели для активностей"""
    __tablename__ = "week"

    id: Mapped[int] = mapped_column(primary_key=True)
    week_day: Mapped[str] = mapped_column(String(2))
    activities: Mapped[List["Activity"]] = relationship(
        secondary=activity_mtm_week,
        back_populates="weeks"
    )

    @property
    def serialize(self):
        return {
            'id': self.id,
            'week_day': self.week_day
        }


class Activity_day(Base):
    """Активность по дням"""
    __tablename__ = "activity_day"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    day: Mapped[datetime.date] = mapped_column(Date)
    activity_id: Mapped[int] = mapped_column(ForeignKey('activity.id'))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'is_done': self.is_done,
            'day': self.day,
            'activity_id': self.activity_id,
        }


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


if session.query(Week).count() == 0:
    """Создание в БД дней недели если их нет"""
    for x in ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']:
        one_weak = Week(week_day=x)
        session.add(one_weak)
        session.commit()

    week_list = session.query(Week.id, Week.week_day).all()
    for week in week_list:
        print(f'id: {week[0]}, name: {week[1]}')
