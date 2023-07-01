import re
from datetime import date

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