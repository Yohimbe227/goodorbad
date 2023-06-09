from django.core.management import BaseCommand

from telegrambot.creation import bot


async def shutdown() -> None:
    """Entry point."""

    await bot.stop_polling()


class Command(BaseCommand):
    def handle(self, *args, **options):
        await shutdown()
