from aiogram import Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Dispatcher

from telegrambot.costants import TELEGRAM_TOKEN
from telegrambot.utils import check_tokens

storage = MemoryStorage()

check_tokens(TELEGRAM_TOKEN)
bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher(storage=storage)
