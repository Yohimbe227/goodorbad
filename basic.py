import logging

from aiogram import types
from aiogram.dispatcher.filters import IDFilter
from aiogram.utils import executor

from creation import bot, dp
from database import sqllite_db
from decorators import func_logger
from exceptions import SendMessageError
from handlers import admin, client, other
from utils import logger
from moderator import IsCurseMessage


def main() -> None:
    """Основная логика работы бота."""

    async def on_startup(_):
        sqllite_db.sql_start()

        logger.info('Бот запущен!')

    dp.filters_factory.bind(IsCurseMessage)
    client.register_handlers_client(dp)
    admin.register_handlers_admin(dp)
    other.register_handlers_other(dp)
    # dp.bind_filter(IsAdmin)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    main()
