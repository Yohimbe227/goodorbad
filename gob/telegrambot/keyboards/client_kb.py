from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

NUMBER_OF_COLUMNS_KB = 4

button_start = KeyboardButton('Старт')
button_about = KeyboardButton('О боте')
button_nearest_place = KeyboardButton('Ближайшее место для...')
button_read_review = KeyboardButton('Узнать отзывы')
button_add_review = KeyboardButton('Добавить отзыв')
button_HR = KeyboardButton('Я HR и мне нравится!')

kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_start.add(button_start)

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client.add(button_start, button_about).add(button_nearest_place).add(
    button_read_review,
    button_add_review,
    button_HR,
)

kb_client_with_places = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
)


def get_keyboard(
    buttons: list[str],
):
    """Create keyboard object by names of buttons.

    Args:
        buttons: Names of needed buttons.

    Returns:
        Keyboard object.

    """
    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    keyboard.add(*[KeyboardButton(button.capitalize()) for button in buttons])
    return keyboard


kb_client_location = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=True,
).add(
    KeyboardButton('Отправить локацию', request_location=True),
)

kb_place_client_next = get_keyboard(
    [
        'Второе',
        'Третье',
        'Больше заведений!',
        'отмена',
    ],
)
