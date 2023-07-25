import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage


from bot.handlers import common, cb_parent, cb_child_activity, cb_child, cb_add_one_more_parent,\
    cb_add_child

from bot.handlers.apshed import send_message_cron_middleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from conf import TELEGRAM_TOKEN

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Старт"),
        BotCommand(command="/info", description="Описание бота"),
        BotCommand(command="/cancel", description="Отменить текущее действие")
    ]
    await bot.set_my_commands(commands)


async def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")


    bot = Bot(token=TELEGRAM_TOKEN, parse_mode="HTML")
    dp = Dispatcher(storage=MemoryStorage())

    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(send_message_cron_middleware, 'cron', hour=10, minute=47, kwargs={'bot': bot})


    dp.include_router(common.router)
    dp.include_router(cb_parent.router)
    dp.include_router(cb_child_activity.router)
    dp.include_router(cb_child.router)
    dp.include_router(cb_add_one_more_parent.router)
    dp.include_router(cb_add_child.router)
    
    await set_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)

    scheduler.start()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error('Bot stopped!')