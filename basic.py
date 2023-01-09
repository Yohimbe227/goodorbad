import logging
import os
import time
from http import HTTPStatus
from logging import StreamHandler
from typing import Union

import requests
# import telegram
from dotenv import load_dotenv

from exceptions import HTTPError, SendMessageError, StatusError, TokenError
from decorators import func_logger
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 6  # 10 минут, 60*10
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

MESSAGE_ERROR_CURRENT_DATE_KEY = (
    'по ключу `{current_date}` возвращается не тип данных "int"'
)
MESSAGE_ERROR_DICT = 'Отклик не является словарем'
MESSAGE_ERROR_HOMEWORKS_KEY = 'По ключу `{homeworks}` передается не список'
MESSAGE_ERROR_HOMEWORKS_NONE = 'Ключ `{homework_name}` не обнаружен'
MESSAGE_ERROR_REQUEST = 'Ошибка запроса'

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}
notoken = [
    token
    for token in ('PRACTICUM_TOKEN', 'TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')
    if globals().get(token) is None
]

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s, %(levelname)s, %(message)s, %(funcName)s',
    )
    logger = logging.getLogger(__name__)


@func_logger('Проверка токенов')
def check_tokens() -> None:
    """Доступность токенов в переменных окружения.

    Raises:
        TokenError: отстутствует какой либо из необходимых токенов.
    """
    if notoken:
        logger.critical('Необходимый токен: %s не обнаружен', notoken)
        raise TokenError(notoken)


# @func_logger('Отправка сообщений в телеграм')
# def send_message(bot: Bot, message: Union[str, Exception]) -> None:
#     """
#     Отправляет сообщения в телеграм.
#
#     Args:
#         bot: объект телеграм бота
#         message: передаваемое сообщение или ошибка
#
#     Raises:
#         SendMessageError: Если ошибка отправки сообщения через телеграм
#     """
#     try:
#         bot.send_message(TELEGRAM_CHAT_ID, message)
#     except Exception as err:
#         logging.exception('Сообщение не отправлено')
#         raise SendMessageError from err
#     logger.debug('Сообщение в телеграмм отправлено')


@func_logger('Получение ответа API')
def get_api_answer(timestamp: int) -> dict:
    """Получаем ответ от эндпоинта.

    Args:
        timestamp: Текущее время в unix формате.

    Returns:
        Резульаты опроса API.

    Raises:
        HTTPError: Ошибка доступа к эндпоинту.
    """
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params={'from_date': timestamp},
        )
    except requests.RequestException as err:
        logging.exception(MESSAGE_ERROR_REQUEST)
        raise HTTPError from err

    if response.status_code != HTTPStatus.OK:
        logger.error(MESSAGE_ERROR_REQUEST)
        raise HTTPError
    return response.json()


@func_logger('Проверка формата ответа API')
def check_response(response: dict) -> dict:
    """Проверка ответа эндпоинта на соответствие документации API.

    Args:
        response: Проверяемый словарь.

    Returns:
        Проверенный словарь.

    Raises:
        TypeError: Ошибка несоответствия типа данных ожидаемому.
    """
    if not isinstance(response, dict):
        logger.error(MESSAGE_ERROR_DICT)
        raise TypeError(MESSAGE_ERROR_DICT)

    if not isinstance(response.get('current_date'), int):
        logger.error(MESSAGE_ERROR_CURRENT_DATE_KEY)
        raise TypeError(MESSAGE_ERROR_CURRENT_DATE_KEY)

    if not isinstance(response.get('homeworks'), list):
        logger.error(MESSAGE_ERROR_HOMEWORKS_KEY)
        raise TypeError(MESSAGE_ERROR_HOMEWORKS_KEY)
    return response


@func_logger('Извлечение статуса работы')
def parse_status(homework: dict) -> str:
    """Получение строки для отправки телеграм.

    Args:
        homework: Сведения о домашней работе.

    Returns:
        Отформатированная строка для отправки в телеграм.

    Raises:
        StatusError: Несоответствие статуса домашней работы ожидаемому.
        NameError: Отсутствие ключа `{homework_name}` в словаре `{homework}`.
    """
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS or status is None:
        logger.error('Неожиданный статус домашней работы: %s', status)
        raise StatusError
    if homework.get('homework_name') is None:
        logger.error(MESSAGE_ERROR_HOMEWORKS_NONE)
        raise NameError(MESSAGE_ERROR_HOMEWORKS_NONE)
    return (
        'Изменился статус проверки работы '
        f'"{homework.get("homework_name")}". '
        f'{HOMEWORK_VERDICTS.get(homework.get("status"))}'
    )


def main() -> None:
    """Основная логика работы бота."""
    check_tokens()
    bot = Bot(token=TELEGRAM_TOKEN)
    # send_message(bot, 'проверка')
    dp = Dispatcher(bot)

    @dp.message_handler()
    async def echo_send(message: types.Message):
        # await message.answer(message.text)
        # await message.reply(message.text)
        await bot.send_message(message.from_user.id, message.text)

    executor.start_polling(dp, skip_updates=True)



if __name__ == '__main__':
    main()
