from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

NUMBER_OF_COLUMNS_KB = 4

button_start = KeyboardButton('/start')
button_about = KeyboardButton('/о_боте')
button_nearest_place = KeyboardButton('/ближайшее_место_для...')
button_read_review = KeyboardButton('/узнать_отзывы')
button_add_review = KeyboardButton('/добавить_отзыв')

kb_start = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_start.add(button_start)

kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_client.add(button_start, button_about).add(button_nearest_place).add(
    button_read_review,
    button_add_review,
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
    KeyboardButton('отправить локацию', request_location=True),
)

kb_place_client_next = get_keyboard(
    [
        'Второе',
        'Третье',
        'Больше заведений!',
        'отмена',
    ],
)
