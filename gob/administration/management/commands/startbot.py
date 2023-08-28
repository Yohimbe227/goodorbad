from django.core.management import BaseCommand

from telegrambot.creation import dp, bot
from telegrambot.handlers import admin
    # other
# from telegrambot.handlers.clients import FSM_nearest_place, FSM_review, basic
# from telegrambot.moderator import IsCurseMessage
# from telegrambot.utils import logger


def starts_bot() -> None:
    """Entry point."""

    # async def on_startup(_):
    #     logger.info('Бот запущен!')

    # dp.filters_factory.bind(IsCurseMessage)
    # basic.register_handlers_client(dp)
    # FSM_review.register_handlers_fsm(dp)
    # FSM_nearest_place.register_handlers_nearest_place(dp)
    # other.register_handlers_other(dp)
    dp.include_router(admin.router)
    bot.delete_webhook(drop_pending_updates=True)
    # dp.start_polling(bot)


class Command(BaseCommand):
    def handle(self, *args, **options):
        starts_bot()
