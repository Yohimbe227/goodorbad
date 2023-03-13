from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup,
                           ReplyKeyboardRemove)

NUMBER_OF_COLUMNS = 4

b1 = KeyboardButton('/start')
b2 = KeyboardButton('/help')
# b4 = KeyboardButton('/Поделиться номером', request_contact=True)
b5 = KeyboardButton('/Отправить_мое_местоположение', request_location=True)
b6 = KeyboardButton('/ближайшее_место_для...')
b7 = KeyboardButton('/добавить_отзыв')
BUTTONS_PLACE_TYPE = ('Бар', 'Ресторан', 'Кафе', 'Пиццерия', 'Фастфуд', 'Суши бар', 'Кофейня', 'Караоке')

kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_start.add(b1)

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client.add(b1).add(b2).insert(b5).row(b6, b7)

kb_client_with_places = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
for number, button in enumerate(BUTTONS_PLACE_TYPE, start=1):
    if number and number % NUMBER_OF_COLUMNS == 0:
        kb_client_with_places.add(button)
    kb_client_with_places.insert(button)


kb_start.add(b1)
