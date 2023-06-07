"""
Buttons with cities for quick dialing.
"""
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from telegrambot.costants import CITIES_KEYBOARD, NUMBER_OF_COLUMNS

buttons = {city: KeyboardButton(city) for city in CITIES_KEYBOARD}

kb_city = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

for number, button in enumerate(buttons, start=1):
    if number % NUMBER_OF_COLUMNS:
        kb_city = kb_city.insert(button)
    else:
        kb_city = kb_city.add(button)
