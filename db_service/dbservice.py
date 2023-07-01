import locale, sys


sys.path.append("..")
from db_service.dbworker import Child, Parent, Week, Activity, Activity_day, engine, session,\
    child_mtm_parent

locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))


def is_parent_in_db(bot_user_id: int):
    """Поиск в БД есть ли такой пользователь"""
    parent = session.query(Parent).filter(Parent.bot_user_id == bot_user_id).first()
    if parent is None: return None
    else: return parent.serialize


def add_parent_and_child(info):
    """Добавление нового родителя и его ребенка + добавление связи м-т-м между ними"""
    parent = Parent(
        name = info.name,
        sex = info.sex,
        bot_user_id = info.bot_user_id,
        phone = info.phone_number,
    )
    child = Child(
        name=info.child_name,
        sex=info.child_sex,
        phone = info.child_number,
    )
    session.add_all([child, parent])
    session.commit()

    parent_ph = session.query(Parent).filter(Parent.phone == info.phone_number).first()
    child_ph = session.query(Child).filter(Child.phone == info.child_number).first()
    child_ph.parents.append(parent_ph)
    session.commit()
    info_db = session.query(Parent).filter(Parent.phone == info.phone_number).first()
    return info_db.serialize
