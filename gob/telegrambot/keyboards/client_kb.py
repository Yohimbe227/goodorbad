from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

NUMBER_OF_COLUMNS_KB = 4

b1 = KeyboardButton('/start')
b2 = KeyboardButton('/help')
b5 = KeyboardButton('/ближайшее_место_для...')
b6 = KeyboardButton('/узнать_отзывы')
b7 = KeyboardButton('/добавить_отзыв')


kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_start.add(b1)

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client.add(b1, b2).add(b5).add(b6, b7)

kb_client_with_places = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
)


def get_keyboard(
    buttons: tuple[
        str,
    ],
):
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    )
    keyboard.add(*[KeyboardButton(button) for button in buttons])
    return keyboard


kb_client_location = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True
).add(
    KeyboardButton('отправить локацию', request_location=True),
)

kb_place_client_next = get_keyboard(('/Второй', '/Третий', '/Следующая тройка',))
