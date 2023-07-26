import sys
from aiogram import Bot

sys.path.append("..")
from db_service.dbservice import ParentDB


async def send_message_cron_middleware(bot: Bot):
    parents = ParentDB.get_bot_user_id_is_active()
    for user_id in parents:
        await bot.send_message(user_id[0], f'Это сообщение отправляется 1 раз в день в определенное время')