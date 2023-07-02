import re
from datetime import date
from tabulate import tabulate

from db_service.dbservice import child_activity_by_day

def valid_number(number: str):
    """Проверка номера на валидность"""
    num = ''.join([x for x in number if x.isdigit()])
    if len(num) == 11: num = '7' + num[1:]
    elif len(num) == 10: num = '7' + num
    try:
        result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', num)
        if bool(result): return num
        else: return False
    except TypeError: return False


def report_table_child(info):
    text = f'Ребенок: {info.name}\n\n'
    activity = []
    for act in info.activities:
        weeks_activity = child_activity_by_day(act.id)
        lst = [act.name, act.percent_complete, act.cost, act.max_cost]
        activity.append(lst + weeks_activity)
    table = tabulate(activity, headers=['Задание', '%', 'cost', 'max_cost', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'])
    return text + table