"""
Buttons with cities for quick dialing.
"""

from telegrambot.costants import CITIES_KEYBOARD, NUMBER_OF_COLUMNS
from telegrambot.keyboards.client_kb import get_keyboard

kb_city = get_keyboard(CITIES_KEYBOARD, columns=3)
