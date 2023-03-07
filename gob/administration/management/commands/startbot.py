from aiogram.utils import executor
from django.core.management import BaseCommand

from telegrambot.creation import dp
from telegrambot.database import sqllite_db
from telegrambot.handlers import other, admin, client
from telegrambot.utils import logger
from telegrambot.moderator import IsCurseMessage


def starts_bot() -> None:
    """Основная логика работы бота."""

    async def on_startup(_):
        sqllite_db.sql_start()

        logger.info('Бот запущен!')

    dp.filters_factory.bind(IsCurseMessage)

    client.register_handlers_client(dp)
    admin.register_handlers_admin(dp)
    other.register_handlers_other(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


class Command(BaseCommand):
    def handle(self, *args, **options):
        starts_bot()

# starts_bot()
