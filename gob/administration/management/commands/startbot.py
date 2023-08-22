from django.core.management import BaseCommand

from aiogram.utils import executor

from telegrambot.creation import dp
from telegrambot.handlers import admin, other
from telegrambot.handlers.clients import FSM_nearest_place, FSM_review, basic
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import logger


def starts_bot() -> None:
    """Entry point."""

    async def on_startup(_):
        logger.info('Бот запущен!')

    dp.filters_factory.bind(IsCurseMessage)
    basic.register_handlers_client(dp)
    FSM_review.register_handlers_fsm(dp)
    FSM_nearest_place.register_handlers_nearest_place(dp)
    admin.register_handlers_admin(dp)
    other.register_handlers_other(dp)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


class Command(BaseCommand):
    def handle(self, *args, **options):
        starts_bot()
