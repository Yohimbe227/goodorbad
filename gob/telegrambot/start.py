import asyncio
import os

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gob.settings")
django.setup()

from telegrambot.creation import dp, bot
from telegrambot.handlers.admin import router as admin_router
from telegrambot.handlers.other import router as other_router
from telegrambot.handlers.clients.basic import start_router as basic_router
from telegrambot.handlers.clients import FSM_nearest_place, FSM_review


async def main():
    await FSM_nearest_place.register_handlers_nearest_place(dp)
    await FSM_review.register_handlers_review(dp)
    dp.include_router(admin_router)
    dp.include_router(basic_router)
    dp.include_router(other_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
