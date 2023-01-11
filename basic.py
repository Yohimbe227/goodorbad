import logging
import os

from dotenv import load_dotenv

from creation import dp, bot
from exceptions import HTTPError, SendMessageError, StatusError, TokenError
from decorators import func_logger
from aiogram.utils import executor

from handlers import client, admin, other
from database import sqllite_db

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

notoken = [
    token
    for token in ('TELEGRAM_TOKEN', 'TELEGRAM_CHAT_ID')
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


def main() -> None:
    """Основная логика работы бота."""
    check_tokens()

    async def on_startup(_):
        print('Бот вышел в онлайн')
        sqllite_db.sql_start()

    client.register_handlers_client(dp)
    admin.register_handlers_admin(dp)
    other.register_handlers_other(dp)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    main()
