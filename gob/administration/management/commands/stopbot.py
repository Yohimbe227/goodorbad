from django.core.management import BaseCommand

from aiogram.utils import executor

from telegrambot.creation import bot, dp
from telegrambot.handlers import admin, other
from telegrambot.handlers.clients import FSM_nearest_place, FSM_review, basic
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import logger


async def shutdown() -> None:
    """Entry point."""

    bot.stop_polling()


class Command(BaseCommand):
    def handle(self, *args, **options):
        shutdown()
