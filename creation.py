import logging
import os

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from decorators import func_logger
from exceptions import TokenError
from utils import check_tokens

storage = MemoryStorage()

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ID = int(os.getenv('ID'))

check_tokens(TELEGRAM_TOKEN)

bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=storage)
