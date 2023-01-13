import logging
from typing import Any

from aiogram import types
from aiogram.bot import bot

from decorators import func_logger
from exceptions import TokenError, SendMessageError


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
async def send_message(mybot: bot, message: types.Message, message_text, **kwargs: Any) -> None:
    """
    Отправляет сообщения в телеграм.

    Включает логирование и обработку ошибок.

    Args:
        mybot: объект телеграм бота
        message: передаваемое сообщение или ошибка
        message_text: текст отправляемого сообщения
    Raises:
        SendMessageError: Если ошибка отправки сообщения через телеграм
    """
    try:
        await mybot.send_message(message.from_user.id, message_text, **kwargs)
    except Exception as err:
        logging.exception('Сообщение не отправлено')
        raise SendMessageError from err
