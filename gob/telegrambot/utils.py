import logging
from typing import Any

from aiogram import types
from aiogram.bot import bot

from telegrambot.decorators import func_logger
from telegrambot.exceptions import SendMessageError, TokenError

# from telegrambot.handlers.clients.basic import NUMBER_OF_PLACES_TO_SHOW

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


async def n_max(array: list, number_of_maximum: int) -> list:
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
            if index and array[index - 1][1] < array[index][1]:
                array[index], array[index - 1] = (
                    array[index - 1],
                    array[index],
                )
        quantity -= 1

    return array[len(array) - number_of_maximum :]


# def place_send_message(message: types.Message, places: list[str], distance: list[float]):
#
#     f'Вот {NUMBER_OF_PLACES_TO_SHOW} заведения и первое из них на карте: \n-' + '\n-'.join(
#         places),


def convert_time(time_work: str) -> str:
    if time_work == '24:00':
        return '00:00'
    return time_work
