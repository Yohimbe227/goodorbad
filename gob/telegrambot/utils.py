import logging
from typing import Any

from aiogram import types
from aiogram.bot import bot

from administration.models import Place
from telegrambot.costants import M_IN_KM, MAX_RANGE_SEARCH
from telegrambot.decorators import func_logger
from telegrambot.exceptions import SendMessageError, TokenError
from telegrambot.keyboards.client_kb import (kb_client_location,
                                             kb_place_client_next)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s, %(funcName)s',
)
logger = logging.getLogger(__name__)


@func_logger('Проверка токенов')
def check_tokens(token) -> None:
    """Доступность токенов в переменных окружения.

    Args:
        token: Токен телеграм бота.

    Raises:
        TokenError: Отстутствует какой либо из необходимых токенов.

    """
    notoken = 'TELEGRAM_TOKEN' if token is None else None
    if notoken:
        logger.critical('Необходимый токен: %s не обнаружен', notoken)
        raise TokenError(notoken)


@func_logger('Отправка сообщения в телеграм', level='info')
async def send_message(
    mybot: bot,
    message: types.Message,
    message_text,
    **kwargs: Any,
) -> None:
    """Отправляет сообщения в телеграм.

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
            message.from_user.id,
            message_text,
            parse_mode='HTML',
            **kwargs,
        )
    except Exception as err:
        logging.exception('Сообщение не отправлено')
        raise SendMessageError from err


async def n_max(
    array: list[str, float],
    number_of_maximum: int,
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
    """Convert time format of API 2gis to standart time format.

    This is only changes '24:00' to '00:00'.

    Args:
        time_work: Time to convert.

    Returns:
        Converted time.

    """
    if time_work == '24:00':
        return '00:00'
    return time_work


def extract_city(city_string: str) -> str:
    return city_string.split(', ')[-2]


def extract_address(address_string):
    _address = ', '.join(address_string.split(', ')[:-1])
    return _address


async def send_message_with_list_of_places(
    message: types.Message,
    mybot: bot,
    number_of_places_to_show: int,
    _nearest_place: list[str, float],
    _place_to_send: list[Place],
) -> None:
    """Send formatted message and message with location to user.

    Args:
        message: `message` object from user.
        mybot: `bot` object.
        number_of_places_to_show: Number of places to show in message to user.
        _nearest_place: objects `Place`, nearest by distance to the user's
            location.
        _place_to_send: `Place` objects for become location and sending
            to user.

    """
    if _nearest_place[0][2] > MAX_RANGE_SEARCH:
        await send_message(
            mybot,
            message,
            'Скорей всего Вы использовали ручной'
            ' ввод адресса и сделали это не '
            'очень круто, проще и надежней использовать кнопочку'
            ' "Отправить локацию"',
            reply_markup=kb_client_location,
        )
    else:
        await send_message(
            mybot,
            message,
            f'Вот {number_of_places_to_show} заведения и первое из них на '
            f'<b>карте</b>: \n-> '
            + '\n-> '.join(
                [
                    str(round(_distance * M_IN_KM))
                    + ' м.: <b>'
                    + place
                    + '</b>'
                    for _, place, _distance in _nearest_place
                    if _distance
                ],
            ),
            reply_markup=kb_place_client_next,
        )
        await mybot.send_location(
            message.from_user.id,
            _place_to_send[0].latitude,
            _place_to_send[0].longitude,
        )


async def send_message_with_place_name(
    mybot: bot,
    message: types.Message,
    place_name_: str,
    place_to_send: list[Place],
) -> None:
    """Send message with place name and message with location to user.

    Args:
        mybot: `bot` object.
        message: `message` object from user.
        place_name_: `Place` name.
        place_to_send: `Place` objects for become location and sending
            to user.

    """

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
