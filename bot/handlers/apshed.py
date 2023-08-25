import datetime
import sys
from aiogram import Bot

sys.path.append("..")
from db_service.dbservice import ActivityDB, ActivityDayDB, change_to_current_weeks_task, ChildDB


async def send_message_cron_middleware(bot: Bot):
    children = ChildDB.get_all_with_bot_user_id()
    for child in children:
        try:
            activities = ActivityDayDB.get_all_activity_for_day(child_id=child[0], day=datetime.date.today())
            activity_text = f'Добрый день {child[2]}\nНа сегодня у вас:'
            if activities:
                for activity in activities:
                    activity_text += f'\n{activity[0]}'
            else:
                activity_text += '\nНет заданий'
            await bot.send_message(child[1], f'{activity_text}')
        except:
            pass


async def create_activity_days_for_next_week(bot: Bot):
    """Добавление activity_day в наступающую неделю"""
    activities = ActivityDB.get_all_id()
    day = datetime.datetime.today() + datetime.timedelta(days=1)
    for activity in activities:
        change_to_current_weeks_task(activity_id=activity[0], day=day)