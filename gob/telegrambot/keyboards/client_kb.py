from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)

b1 = KeyboardButton('/start')
b2 = KeyboardButton('/help')
b3 = KeyboardButton('/о_боте')
b4 = KeyboardButton('/Поделиться номером', request_contact=True)
b5 = KeyboardButton('/Отправить_мое_местоположение', request_location=True)
b6 = KeyboardButton('/место')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client.add(b1).add(b2).insert(b3).row(b4, b5, b6)
