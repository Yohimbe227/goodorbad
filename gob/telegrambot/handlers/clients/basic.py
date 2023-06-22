from asyncio import sleep
from datetime import datetime

from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError

from aiogram import types
from aiogram.dispatcher import Dispatcher
from asgiref.sync import sync_to_async

from administration.models import User
from telegrambot.costants import START_MESSAGE, ID
from telegrambot.creation import bot
from telegrambot.database import database_functions
from telegrambot.decorators import func_logger
from telegrambot.exceptions import UnknownError
from telegrambot.keyboards.client_kb import kb_client
from telegrambot.utils import send_message


async def command_start(message: types.Message) -> None:
    """Initial Login to the System.

    Creates or updates the user using the data from `message`.
    A welcome message is issued.

    Args:
        message: `message` object from user.

    Raises:
        UnknownError: if any problem with get or creation of user.

    """
    _params_user = {
        'username': message.from_user.id,
        'last_name': message.from_user.last_name,
        'first_name': message.from_user.first_name,
    }
    params_user = {key: value for key, value in _params_user.items() if value}

    try:
        author, created = await User.objects.aget_or_create(**params_user)
        author.last_login = datetime.now()
        await sync_to_async(author.save)()
    except (MultipleObjectsReturned, IntegrityError) as error:
        raise UnknownError(error)
    if created:
        await send_message(
            bot,
            message,
            START_MESSAGE.format(username=message.from_user.first_name),
            reply_markup=kb_client,
        )
        await message.delete()
    else:
        await send_message(
            bot,
            message,
            f'И снова здравствуйте {message.from_user.first_name}!',
            reply_markup=kb_client,
        )


@func_logger('вывод всех заведений', level='info')
async def _places_all(message: types.Message) -> None:
    """Output of all places.

    Args:
        message: Aiogram message object.

    Notes: Only for tests on small bases!!! Telegram can ban you for spam!!!
    """

    await database_functions.read_all_data_from_base(message)


@func_logger('вывод сообщения о боте', level='info')
async def about_bot(message: types.Message) -> None:
    """Отсылает сообщение с описанием основного функционала бота.

    Args:
        message: `message` object from user.

    """
    await send_message(
        bot,
        message,
        'Этот бот подскажет тебе где поблизости находятся интересные '
        'заведения: <b>бары, кафе, рестораны</b> и т.п. \nТакже вы можете '
        'посмотреть/добавить отзывы об выбранном заведении! \n Если вдруг'
        'что-то непонятно, то набери "отмена" или просто жми на клавиатуре и '
        'начнем сначала!',
        reply_markup=kb_client,
    )


@func_logger('вывод сообщения HR', level='info')
async def hr_attention(message: types.Message) -> None:
    """Отсылает сообщение с описанием основного функционала бота.

    Args:
        message: `message` object from user.

    """
    await send_message(
        bot,
        message,
        'Спасибо за интерес, жуть как приятно, встретимся на собесе :)',
        reply_markup=kb_client,
    )
    await sleep(3)
    await send_message(
        bot,
        message,
        'Ну или нет :(',
        reply_markup=kb_client,
    )
    await bot.send_message(ID, 'Кто-то заюзал эту функцию, может даже HR')


def register_handlers_client(disp: Dispatcher):
    """Handlers registration."""

    disp.register_message_handler(
        command_start,
        commands=['start', 'старт'],
    )
    disp.register_message_handler(
        about_bot,
        commands=[
            'о_боте',
            'about',
        ],
    )
    disp.register_message_handler(_places_all, commands=['место'])
    disp.register_message_handler(hr_attention, commands=['Я_HR_и_мне_нравится'])
