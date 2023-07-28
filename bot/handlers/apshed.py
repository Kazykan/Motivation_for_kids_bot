import datetime
import sys
from aiogram import Bot

sys.path.append("..")
from db_service.dbservice import ActivityDB, ParentDB, change_to_current_weeks_task


async def send_message_cron_middleware(bot: Bot):
    parents = ParentDB.get_bot_user_id_is_active()
    for user_id in parents:
        await bot.send_message(user_id[0], f'Это сообщение отправляется 1 раз в день в определенное время')


async def create_activity_days_for_next_week(bot: Bot):
    """Добавление activity_day в наступающую неделю"""
    activities = ActivityDB.get_all_id()
    day = datetime.datetime.today() + datetime.timedelta(days=1)
    for activity in activities:
        change_to_current_weeks_task(activity_id=activity[0], day=day)