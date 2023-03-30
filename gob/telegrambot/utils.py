import logging
from typing import Any

from aiogram import types
from aiogram.bot import bot

from administration.models import Place
from telegrambot.costants import M_IN_KM
from telegrambot.decorators import func_logger
from telegrambot.exceptions import SendMessageError, TokenError
from telegrambot.keyboards.client_kb import kb_place_client_next

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s, %(funcName)s',
)
logger = logging.getLogger(__name__)


@func_logger('Проверка токенов')
def check_tokens(token) -> None:
    """Доступность токенов в переменных окружения.

    Raises:
        TokenError: отстутствует какой либо из необходимых токенов.
    """
    notoken = 'TELEGRAM_TOKEN' if token is None else None
    if notoken:
        logger.critical('Необходимый токен: %s не обнаружен', notoken)
        raise TokenError(notoken)


@func_logger('Отправка сообщения в телеграм', level='info')
async def send_message(
    mybot: bot, message: types.Message, message_text, **kwargs: Any
) -> None:
    """
    Отправляет сообщения в телеграм.

    Включает логирование и обработку ошибок.

    Args:
        mybot: объект телеграм бота.
        message: передаваемое сообщение или ошибка.
        message_text: текст отправляемого сообщения.
    Raises:
        SendMessageError: Если ошибка отправки сообщения через телеграм.

    """
    try:
        await mybot.send_message(
            message.from_user.id, message_text, parse_mode='HTML', **kwargs
        )
    except Exception as err:
        logging.exception('Сообщение не отправлено')
        raise SendMessageError from err


async def n_max(
    array: list[str, float], number_of_maximum: int
) -> list[str, float]:
    """Find needed quantity of minimum elements in array.

    Args:
        array: The array in which we are looking for elements.
        number_of_maximum: The number of minimum elements.

    Returns:
        The array of minimum elements in descending order.

    """
    quantity = len(array)
    while quantity > len(array) - number_of_maximum:
        for index in range(quantity):
            if index and array[index - 1][2] < array[index][2]:
                array[index], array[index - 1] = (
                    array[index - 1],
                    array[index],
                )
        quantity -= 1
    result = array[len(array) - number_of_maximum :]
    return list(reversed(result))


def convert_time(time_work: str) -> str:
    if time_work == '24:00':
        return '00:00'
    return time_work


async def send_message_with_list_of_places(
    message: types.Message,
    mybot,
    number_of_places_to_show,
    nearest_place,
    place_to_send_,
):
    await send_message(
        mybot,
        message,
        f'Вот еще {number_of_places_to_show} заведения и первое из них на <b>карте</b>: \n-> '
        + '\n-> '.join(
            [
                str(round(distance_ * M_IN_KM)) + ' м.: <b>' + place + '</b>'
                for _, place, distance_ in nearest_place
            ]
        ),
        reply_markup=kb_place_client_next,
    )
    await mybot.send_location(
        message.from_user.id,
        place_to_send_[0].latitude,
        place_to_send_[0].longitude,
    )


async def send_message_with_place_name(
    mybot: bot,
    message: types.Message,
    place_name_: str,
    place_to_send: list[Place],
):
    await send_message(
        mybot,
        message,
        place_name_,
        reply_markup=kb_place_client_next,
    )
    await mybot.send_location(
        message.from_user.id,
        place_to_send[0].latitude,
        place_to_send[0].longitude,
    )
