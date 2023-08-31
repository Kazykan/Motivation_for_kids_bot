import datetime
import re, locale
from datetime import date, timedelta

from db_service.pydantic_model import Activity_serialize

# locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def valid_number(number: str):
    """Проверка номера на валидность"""
    num = ''.join([x for x in number if x.isdigit()])
    if len(num) == 11:
        num = '7' + num[1:]
    elif len(num) == 10:
        num = '7' + num
    try:
        result = re.match(
            r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', num)
        if bool(result):
            return num
        else:
            return False
    except TypeError:
        return False


def get_child_gender_emoji(sex: int) -> str:
    if sex == 2:
        return '👧🏽'
    return '👦🏽'


def is_weekday_on(week_dict: list) -> dict:
    """Берем исходный список недель и заменяем в нем активные недели"""
    source_dict = {1: '❌', 2: '❌',
                   3: '❌', 4: '❌',
                   5: '❌', 6: '❌', 7: '❌'}
    if not week_dict:
        return source_dict
    all = {}
    for x in week_dict:
        x_dict = {x.week_id: x.week}
        temp_dict = all | x_dict
        all = temp_dict.copy()
    return ({**source_dict, **all})


def split_by_week_day(week_list):
    source_dict = {1: '-', 2: '-',
                   3: '-', 4: '-',
                   5: '-', 6: '-', 7: '-'}
    all = {}
    for week_day in week_list:
        day_dict = {week_day.week_id: week_day.week}
        temp_dict = all | day_dict
        all = temp_dict.copy()
    return ''.join([week for week in {**source_dict, **all}.values()])


def activity_to_text(activity: Activity_serialize, day=False):
    text = (f'Задание: <b>{activity.name}</b>\n'
            f'Описание: <b>{activity.title}</b>\n'
            f'Стоимость за выполнение: <b>{activity.cost} ₽</b>\n'
            f'Активный дни недели: {split_by_week_day(activity.weeks)}')
    if day:
        this_week = get_this_week(this_day=day)
    else:
        this_week = get_this_week()
    # Сортировка по дате
    days = sorted(activity.activity_days, key=lambda x: x.day)
    for day in days:
        if day.day in this_week:
            text += f'\n{day.day.strftime("%a %d %b")} '

            if day.is_done:
                text += '✅'
            else:
                text += '❌'
    return text


def get_this_week(this_day=False):
    """Получаем даты текущей недели отсортированные"""
    if not this_day:
        this_day = date.today()  # Получаем текущую дату
    week_day = this_day.weekday() + 1  # И день недели
    days_of_current_week = []
    if week_day == 1:
        for x in range(7):
            days_of_current_week.append(this_day + timedelta(days=x))
    else:
        monday = this_day - timedelta(days=(this_day.weekday()))
        for x in range(7):
            days_of_current_week.append(monday + timedelta(days=x))
    return days_of_current_week


def is_day_in_activity_days(activity_day_to_db, day):
    """Проверка есть день в списке activity_day_to_db методом перебора"""
    for act_day in activity_day_to_db:
        if day in act_day:
            return act_day
    return None


def convert_date(day):
    if not day:
        return False
    if day == 'False':
        return False
    if isinstance(day, datetime.date):
        return day.strftime('%Y-%m-%d')
    else:
        temp_day = f'{day} 08:15:27'
        time = datetime.datetime.strptime(temp_day, '%Y-%m-%d %H:%M:%S')
        return time.date()


def valid_name(contact):
    fullname = ''
    if contact.last_name:
        fullname += f'{contact.last_name} '
    if contact.first_name:
        fullname += f'{contact.first_name}'
    if fullname == '':
        pass
    return fullname
