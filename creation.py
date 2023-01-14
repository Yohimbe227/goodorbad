import logging
import os

from aiogram import Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from dotenv import load_dotenv

from decorators import func_logger
from exceptions import TokenError
from utils import check_tokens

storage = MemoryStorage()

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ID = int(os.getenv('ID'))

# Size of city keyboard
NUMBER_OF_ROWS = 2
NUMBER_OF_COLUMNS = 3

check_tokens(TELEGRAM_TOKEN)

bot = Bot(TELEGRAM_TOKEN)
dp = Dispatcher(bot, storage=storage)
