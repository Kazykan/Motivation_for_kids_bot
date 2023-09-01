import locale, sys
from tabulate import tabulate
from datetime import date, timedelta
import math

sys.path.append(".")
from db_service.matplot_diagram import get_diagram_image  # noqa: E402
from db_service.pydantic_model import Child_Base, Child_serialize_activities  # noqa: E402
from db_service.service import convert_date, get_this_week, \
    is_day_in_activity_days  # noqa: E402
from db_service.dbworker import Child, Parent, Week, Activity, Activity_day, \
    session, child_mtm_parent, activity_mtm_week  # noqa: E402
from sqlalchemy import select, and_  # noqa: E402

# locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def add_parent_and_child(info):
    """Добавление нового родителя и его ребенка + добавление связи м-т-м между ними"""
    parent = Parent(
        name=info.name,
        sex=info.sex,
        bot_user_id=info.bot_user_id,
        phone=info.phone_number,
    )
    child = Child(
        name=info.child_name,
        sex=info.child_sex,
        phone=info.child_number,
    )
    session.add_all([child, parent])
    session.commit()

    parent_ph = session.query(Parent).filter(
        Parent.phone == info.phone_number).first()
    child_ph = session.query(Child).filter(
        Child.phone == info.child_number).first()
    child_ph.parents.append(parent_ph)
    session.commit()
    info_db = session.query(Parent).filter(
        Parent.phone == info.phone_number).first()
    return info_db.serialize


def child_activity_by_day(activity_day_id: int, day=False) -> list:
    week_days = get_this_week(this_day=day)
    days = get_activity_days_between_dates(
        activity_day_id=activity_day_id,
        start_date=week_days[0],
        end_date=week_days[-1]
    )
    weeks = ['-', '-', '-', '-', '-', '-', '-']
    for day in days:
        if day.is_done:
            is_done = 'v'
        elif day.is_done == False:
            is_done = 'x'
        week = day.day.weekday()
        weeks[week] = is_done
    weeks.insert(5, ' ')
    return [''.join(weeks)]


def get_weeks_list_for_activities(activity_id):
    """Получаем список дней недели для задания"""
    activity_info = session.query(Activity).filter(
        Activity.id == activity_id).first()
    return activity_info.serialize


def get_activity_day(activity_day_id: int):
    activity_day = session.query(Activity_day).filter(
        Activity_day.id == activity_day_id).first()
    return activity_day.serialize


def get_activity_week(activity_id, week_id):
    stmt = select(Week).where(
        and_(
            Activity.id == activity_id,
            Week.id == week_id,
            Activity.id == activity_mtm_week.c.activity_id,
            Week.id == activity_mtm_week.c.week_id
            ))
    weeks = session.execute(stmt).scalars().first()
    return weeks


def add_activity_week(activity_id, week_id):
    activity = session.query(Activity).filter(Activity.id == activity_id).first()
    week = session.query(Week).filter(Week.id == week_id).first()
    activity.weeks.append(week)
    session.commit()
    change_to_current_weeks_task(activity_id=activity_id)
    return True


def delete_activity_week(activity_id, week_id):
    """Удаление связи между активностью и днем недели"""
    activity = session.query(Activity).filter(
        Activity.id == activity_id).first()
    week = session.query(Week).filter(Week.id == week_id).first()
    activity.weeks.remove(week)
    session.commit()
    change_to_current_weeks_task(activity_id=activity_id)
    return True


def change_to_current_weeks_task(activity_id, day=False):
    """Обновление заданий в текущей неделе, смотри расписание
    по активным дням недели и добавляем задания или удаляем их"""
    stmt = select(Week.id).where(and_(
        Activity.id == activity_id,
        Activity.id == activity_mtm_week.c.activity_id,
        Week.id == activity_mtm_week.c.week_id
    ))

    # Получаем какие дни недели выбраны [1, 3, 5, 6]
    act_week_day = session.execute(stmt).scalars().all()
    # [datetime.date(2023, 7, 17), datetime.date(2023, 7, 18), ...]
    current_week = get_this_week(this_day=day)
    activity_day_to_db = get_activity_days_between_dates(
        activity_day_id=activity_id,
        start_date=current_week[0],
        end_date=current_week[-1])

    for day_of_week in current_week:
        activity_id_to_this_day = is_day_in_activity_days(
            activity_day_to_db=activity_day_to_db,
            day=day_of_week)

        # Есть текущий день в расписании
        if (day_of_week.weekday() + 1) in act_week_day:

            # И его нет в БД, тогда создаем эту запись
            if not activity_id_to_this_day:
                ActivityDayDB.add(activity_id=activity_id, day=day_of_week)

        # Если нет текущего дня в расписании, но он есть в БД - удаляем
        else:
            if activity_id_to_this_day:
                ActivityDayDB.delete(
                    activity_day_id=activity_id_to_this_day[0])
    return True


def get_activity_days_between_dates(
        activity_day_id: int, start_date: date, end_date: date, count=False):
    if count:
        activity_days = session.query(Activity_day).filter(
            and_(
                Activity_day.day.between(start_date, end_date),
                Activity_day.activity_id == activity_day_id)).count()
    else:
        activity_days = session.query(
            Activity_day.id,
            Activity_day.day,
            Activity_day.is_done).filter(
            and_(
                Activity_day.day.between(start_date, end_date),
                Activity_day.activity_id == activity_day_id))
    return activity_days


def report_table_child(child_id: int, day=False):
    child = Child_serialize_activities.validate(
        ChildDB.get_data(child_id=child_id))
    text = f'Ребенок: {child.name}\n\n'
    activity_lst = []
    weekly_days = get_this_week(this_day=day)

    for activity in child.activities:
        weeks_activity = child_activity_by_day(activity.id, day=day)
        weekly_total_payout = get_weekly_total_payout(
            activity_id=activity.id,
            day=day, cost=activity.cost)
        lst = [activity.name, weekly_total_payout]
        activity_lst.append(lst + weeks_activity)

    text += f'Неделя: c {weekly_days[0].strftime("%d %b")}'
    text += f' по {weekly_days[-1].strftime("%d %b")}\n'

    total_payout = f'\nИтоговая выплата: {sum([x[1] for x in activity_lst])} ₽'
    table = tabulate(activity_lst, headers=['Задание', '₽', 'Пн-Пт СбВс'])
    return text + table + total_payout


def get_data_for_diagram_image(child_id: int, day=False):
    child = Child_serialize_activities.validate(
        ChildDB.get_data(child_id=child_id))
    vals_diagram = []
    labels_diagram = []

    for activity in child.activities:
        weekly_total_payout = get_weekly_total_payout(
            activity_id=activity.id,
            day=day, cost=activity.cost)
        vals_diagram.append(weekly_total_payout)
        labels_diagram.append(activity.name)

    if vals_diagram:
        get_diagram_image(
            vals=vals_diagram,
            labels=labels_diagram,
            child_id=child.bot_user_id)
        return True
    else:
        return False


def get_weekly_total_payout(activity_id, day, cost):
    current_week = get_this_week(this_day=day)

    activity_day_to_db = get_activity_days_between_dates(
        activity_day_id=activity_id,
        start_date=current_week[0],
        end_date=current_week[-1])
    count = get_activity_days_between_dates(
        activity_day_id=activity_id,
        start_date=current_week[0],
        end_date=current_week[-1], count=True)

    try:
        one_day_cost = math.ceil(cost / count)
    except ZeroDivisionError:
        one_day_cost = 0
    total_payout = 0
    for activity_day in activity_day_to_db:
        if activity_day[2]:
            total_payout += one_day_cost
    return total_payout


class ParentDB:
    
    @staticmethod
    def add_one_more_parent(data):
        """{'name': 'Марина', 'gender': 2, 'phone': '7962412****',
        'all_children_id': [1]}"""
        parent = Parent(
            name=data['name'],
            phone=data['phone'],
            sex=data['gender']
        )
        session.add(parent)
        session.commit()
        for child_id in data['all_children_id']:  # Добавляем через цикл связь МТМ новый родитель и детей
            child_ph = session.query(Child).filter(Child.id == child_id).first()
            child_ph.parents.append(parent)
            session.commit()
    
    @staticmethod
    def get_or_update_data_by_phone_number(
            phone_number: str,
            bot_user_id: int):
        parent = session.query(Parent).filter(
            Parent.phone == phone_number).first()
        if parent is None:
            return None
        else:
            parent.bot_user_id = bot_user_id
            session.commit()
            return parent.serialize
    
    @staticmethod
    def get_all_parent_id(child_id: int) -> list:
        """ Список id всех родителей"""
        stmt = select(Parent.id).where(and_(
            Child.id == child_id,
            Parent.id == child_mtm_parent.c.parent_id,
            Child.id == child_mtm_parent.c.child_id
        ))
        all_parent_id = session.execute(stmt).scalars().all()
        return all_parent_id

    @staticmethod
    def get_bot_user_id_is_active():
        parents_id = session.query(Parent.bot_user_id).all()
        return parents_id
    
    @staticmethod
    def get_all_bot_users_id(child_id: int) -> list:
        stmt = select(Parent.bot_user_id).where(and_(
            Parent.bot_user_id is not None,
            Child.id == child_id,
            Parent.id == child_mtm_parent.c.parent_id,
            Child.id == child_mtm_parent.c.child_id
        ))
        all_parent_bot_user_id = session.execute(stmt).scalars().all()
        return all_parent_bot_user_id

    @staticmethod
    def is_bot_user_id(bot_user_id: int):
        """Поиск в БД есть такой пользователь"""
        parent = session.query(Parent).filter(
            Parent.bot_user_id == bot_user_id).first()
        if parent is None:
            return None
        else:
            return parent.serialize


class ChildDB:

    @staticmethod
    def add_child(data: Child_Base, all_parent_id: list):
        child = Child(
            name=data.name,
            sex=data.sex,
            phone=data.phone
        )
        session.add(child)
        session.commit()
        # Добавляем через цикл связь МТМ новый родитель и детей
        for parent_id in all_parent_id:
            parent_ph = session.query(Parent).filter(
                Parent.id == parent_id).first()
            parent_ph.children.append(child)
            session.commit()
        return child.serialize

    @staticmethod
    def update(child_id: int, bot_user_id: int):
        """Добавляем данные"""
        child = session.query(Child).filter(Child.id == child_id).first()
        child.bot_user_id = bot_user_id
        session.commit()
        return True
    
    @staticmethod
    def check_is_phone(child_number: str):
        child = session.query(Child).filter(
            Child.phone == child_number).first()
        if child:
            return child.serialize_activities
        else:
            return None
    
    @staticmethod
    def is_bot_user_id(bot_user_id: int):
        """Поиск в БД если такой ребенок"""
        child = session.query(Child).filter(
            Child.bot_user_id == bot_user_id).first()
        if child is None:
            return None
        else:
            return child.id
            
    @staticmethod
    def get_all_children_id(parent_id: int) -> list:
        """ Список id всех родителей"""
        stmt = select(Child.id).where(and_(
            Parent.id == parent_id,
            Parent.id == child_mtm_parent.c.parent_id,
            Child.id == child_mtm_parent.c.child_id
        ))
        all_children_id = session.execute(stmt).scalars().all()
        return all_children_id
    
    @staticmethod
    def get_first_child_id(bot_user_id: int):
        """Вернуть id первого ребенка"""
        stmt = select(Child.id).where(and_(
            Parent.bot_user_id == bot_user_id,
            Parent.id == child_mtm_parent.c.parent_id,
            Child.id == child_mtm_parent.c.child_id
        ))
        one_child_id = session.execute(stmt).scalars().first()
        return one_child_id
    
    @staticmethod
    def get_activity_one(activity_id: int, day=False) -> dict:
        this_week = get_this_week(this_day=day)
        activity = session.query(Activity).filter(
            Activity.id == activity_id).first().serialize
        activity_days_damp = session.query(
            Activity_day.id,
            Activity_day.is_done,
            Activity_day.day).filter(
            and_(
                Activity_day.day.between(this_week[0], this_week[-1]),
                Activity_day.activity_id == activity_id))
        activity_days = []
        for day in activity_days_damp:
            activity_days.append({
                'id': day.id,
                'is_done': day.is_done,
                'day': day.day
                })
        activity['activity_days'] = activity_days
        return activity

    @staticmethod
    def get_data(child_id: int):
        """Данные по ребенку"""
        child_data = session.query(Child).filter(Child.id == child_id).first()
        return child_data.serialize_activities

    @staticmethod
    def get_name(child_id: int):
        child_name = session.query(Child.name).filter(
            Child.id == child_id).first()
        return child_name[0]

    @staticmethod
    def get_all_with_bot_user_id():
        children_id = session.query(
            Child.id,
            Child.bot_user_id,
            Child.name).filter(Child.bot_user_id is not None).all()
        return children_id


class ActivityDB():

    @staticmethod
    def add(info):
        activity = Activity(
            name=info.name,
            title=info.title,
            percent_complete=info.percent_complete,
            cost=info.cost,
            max_cost=info.cost,
            child_id=info.child_id
        )
        session.add(activity)
        session.commit()
        return activity.serialize

    @staticmethod
    def get_all_id():
        activities = session.query(Activity.id).all()
        return activities

    @staticmethod
    def delete_activity(activity_id: int):
        """Delete an activity and all related activityDay"""
        activity = session.query(Activity).filter(
            Activity.id == activity_id).first()
        session.delete(activity)
        session.commit()
        return True

    @staticmethod
    def get_info(activity_id: int):
        activity = session.query(Activity).filter(
            Activity.id == activity_id).first()
        return activity.serialize


class ActivityDayDB():

    @staticmethod
    def info(activity_day_id: int):
        activity_day = session.query(Activity_day).filter(
            Activity_day.id == activity_day_id).first()
        return activity_day.serialize

    @staticmethod
    def is_previous_week(child_id: int, day):
        this_week = get_this_week(this_day=day)
        activity_day = session.query(Activity_day).filter(and_(
            Activity.child_id == child_id,
            Activity_day.activity_id == Activity.id,
            Activity_day.day.between(this_week[0], this_week[-1]),
        )).first()
        return activity_day

    @staticmethod
    def add(activity_id, day):
        activ = Activity_day(
            is_done=False,
            day=day,
            activity_id=activity_id
            )
        session.add(activ)
        session.commit()

    @staticmethod
    def delete(activity_day_id):
        activity_day = session.query(Activity_day).filter(
            Activity_day.id == activity_day_id).first()
        session.delete(activity_day)
        session.commit()

    @staticmethod
    def change_is_done(activity_day_id: int):
        activity_day = session.query(Activity_day).filter(
            Activity_day.id == activity_day_id).first()
        if activity_day.is_done:
            activity_day.is_done = False
        else:
            activity_day.is_done = True
        session.commit()
        return True

    @staticmethod
    def get_all_activity_for_day(child_id, day):
        """Получить все активности на определенный день"""
        activities = session.query(Activity.name).filter(and_(
            Activity.child_id == child_id,
            Activity_day.activity_id == Activity.id,
            Activity_day.day == day
        ))
        if activities.count() == 0:
            return False
        else:
            return activities

    @staticmethod
    def there_is_for_today(activity_id, day=False):
        """Есть эта активность на этот день"""
        if not day:
            day = date.today()
        activity_day = session.query(Activity_day.id).filter(and_(
            Activity_day.activity_id == activity_id,
            Activity_day.day == day
        ))
        if activity_day.count() == 0:
            return False
        else:
            return activity_day[0][0]

    @staticmethod
    def get_activity_name(activity_day_id):
        activity = session.query(Activity.name).filter(and_(
            Activity.id == Activity_day.activity_id,
            Activity_day.id == activity_day_id)).first()
        return activity[0]


def get_navigation_arrows_by_days_of_week(child_id, day):
    """Проверяем есть активности по предыдущей неделе у ребенка,
    если есть добавляем список кнопок"""
    buttons = []

    if day == 'False' or day is False:
        day = date.today()
    else:
        day = convert_date(day=day)

    previous_week = ActivityDayDB.is_previous_week(
        child_id=child_id,
        day=(day - timedelta(days=7))
        )
    next_week = ActivityDayDB.is_previous_week(
        child_id=child_id,
        day=(day + timedelta(days=7))
        )
    previous_week_str = convert_date(day - timedelta(days=7))
    next_week_str = convert_date(day + timedelta(days=7))

    if previous_week and next_week:
        buttons.append({
            'text': '⬅️ previous week',
            'day': previous_week_str,
            'row': 2
            })
        buttons.append({
            'text': 'next week ➡️',
            'day': next_week_str,
            'row': 2
            })
    else:
        if previous_week:
            # Если есть данные по предыдущей неделе добавляем кнопку назад
            buttons.append({
                'text': '⬅️ previous week',
                'day': previous_week_str,
                'row': 1
                })
        if next_week:
            # Если есть данные по следующей неделе добавляем кнопку вперед
            buttons.append({
                'text': 'next week ➡️',
                'day': next_week_str,
                'row': 1
                })
    return buttons
