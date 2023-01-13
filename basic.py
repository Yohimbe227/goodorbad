import logging

from creation import dp, bot
from exceptions import SendMessageError
from decorators import func_logger
from aiogram.utils import executor

from aiogram import types
from handlers import client, admin, other
from database import sqllite_db
from utils import logger


def main() -> None:
    """Основная логика работы бота."""

    async def on_startup(_):
        logger.info('Бот запущен!')
        sqllite_db.sql_start()

    client.register_handlers_client(dp)
    admin.register_handlers_admin(dp)
    other.register_handlers_other(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    main()
