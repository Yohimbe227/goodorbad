from copy import deepcopy

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from telegrambot.costants import NUMBER_OF_COLUMNS, PLACE_TYPES

NUMBER_OF_COLUMNS_KB = 4

button_start = KeyboardButton(text="Старт")
button_about = KeyboardButton(text="О боте")
button_nearest_place = KeyboardButton(text="Ближайшее место для...")
button_read_review = KeyboardButton(text="Узнать отзывы")
button_add_review = KeyboardButton(text="Добавить отзыв")
button_HR = KeyboardButton(text="Я HR и мне нравится!")
button_return = KeyboardButton(text="Вернуться")
button_location = KeyboardButton(
    text="Отправить локацию", request_location=True
)
kb_start = ReplyKeyboardMarkup(
    keyboard=[
        [
            button_start,
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

kb_client = ReplyKeyboardMarkup(
    keyboard=[
        [button_start, button_about],
        [button_nearest_place],
        [
            button_read_review,
            button_add_review,
            button_HR,
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


def get_keyboard(
    buttons: list[str],
    columns=NUMBER_OF_COLUMNS,
):
    """Create keyboard object by names of buttons.

    Args:
        columns: Length of every row.
        buttons: Names of needed buttons.

    Returns:
        Keyboard object.

    """
    row = []
    matrix = []
    for index, button in enumerate(buttons):
        button = KeyboardButton(text=button.capitalize())
        row.append(button)
        if (index + 1) % columns == 0:
            matrix.append(row)
            row = []
    if row:
        matrix.append(row)
    if not matrix and not row:
        return [[]]
    return ReplyKeyboardMarkup(
        keyboard=matrix,
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    #
    #
    # return ReplyKeyboardMarkup(
    #     keyboard=[[KeyboardButton(text=button.capitalize()) for button in buttons]],
    #     resize_keyboard=True,
    #     one_time_keyboard=True,
    # )


kb_client_location = ReplyKeyboardMarkup(
    keyboard=[
        [
            button_location,
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

kb_client_return = deepcopy(kb_client_location)
kb_client_return.keyboard[0].append(button_return)

kb_place_client_next = get_keyboard(
    [
        "Второе",
        "Третье",
        "Больше заведений!",
        "отмена",
    ],
    3,
)

kb_client_categories = get_keyboard(PLACE_TYPES.keys())
