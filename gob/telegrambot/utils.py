import heapq
import logging
from typing import Any

from aiogram import types
from aiogram import Bot

from administration.models import Place
from telegrambot.costants import MAX_RANGE_SEARCH
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
    mybot: Bot,
    message: types.Message,
    message_text: str,
    **kwargs: Any,
) -> None:
    """Sends messages via Telegram.

    Includes logging and error handling.

    Args:
        mybot: Telegram bot object.
        message: Transmitted message or error.
        message_text: The text of the message to be sent.
        kwargs: Another known parameters.

    Raises:
        SendMessageError: If there is an error sending a message via Telegram.

    """
    await mybot.send_message(
        message.from_user.id,
        message_text,
        parse_mode='HTML',
        **kwargs,
    )


async def n_min(
    array: list[tuple[Place, float]],
    number_of_maximum: int,
) -> list[tuple[Place, float]]:
    """Find needed quantity of minimum elements in array.

    Args:
        array: The array in which we are looking for elements.
        number_of_maximum: The number of minimum elements.

    Returns:
        The array of minimum elements in descending order.

    """
    result = heapq.nsmallest(
        number_of_maximum,
        array,
        key=lambda _array: _array[1],
    )
    return result


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
    mybot: Bot,
    number_of_places_to_show: int,
    _nearest_places: list[tuple[Place, float]],
    reply_markup=kb_place_client_next,
) -> None:
    """Send formatted message and message with location to user.

    Args:
        message: `message` object from user.
        mybot: `bot` object.
        number_of_places_to_show: Number of places to show in message to user.
        _nearest_places: Objects `Place`, nearest by distance to the user's
            location.
        reply_markup: Keyboard type.

    """
    if _nearest_places[0][1] > MAX_RANGE_SEARCH:
        await send_message(
            mybot,
            message,
            'Скорей всего Вы использовали ручной ввод адресса и сделали это '
            'не очень круто, проще и надежней использовать кнопочку'
            ' "Отправить локацию"',
            reply_markup=reply_markup,
        )
    else:
        await send_message(
            mybot,
            message,
            f'Вот {number_of_places_to_show} заведения и первое из них на '
            f'<b>карте</b>: \n-> '
            + '\n-> '.join(
                [
                    str(round(_distance)) + ' м.: <b>' + place.name + '</b>'
                    for place, _distance in _nearest_places
                    if _distance
                ],
            ),
            reply_markup=reply_markup,
        )
        await mybot.send_location(
            message.from_user.id,
            _nearest_places[0][0].latitude,
            _nearest_places[0][0].longitude,
        )


def prints(arg):
    print(arg)
