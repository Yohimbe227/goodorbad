import asyncio
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gob.settings")
django.setup()
from telegrambot.creation import dp, bot
from telegrambot.handlers import admin


async def main():
    dp.include_router(admin.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
