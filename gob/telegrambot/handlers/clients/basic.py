from administration.models import Place, Review, User
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import IDFilter, Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import KeyboardButton
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError
from haversine import haversine
from telegrambot.creation import ID, bot
from telegrambot.database import sqllite_db
from telegrambot.database.sqllite_db import (add_review_in_database,
                                             read_review_from_database,
                                             search_place_name_in_database)
from telegrambot.decorators import func_logger
from telegrambot.exceptions import UnknownError
from telegrambot.handlers.admin import cancel_handler
from telegrambot.keyboards.city_kb import kb_city
from telegrambot.keyboards.client_kb import (NUMBER_OF_COLUMNS_KB,
                                             get_keyboard, kb_client,
                                             kb_client_with_places, kb_start)
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import n_max, send_message

START_MESSAGE = (
    'Добро пожаловать {username}. Для удобства нажмите кнопочку'
    '`Отправить мое местоположение`. Тогда мы сможем подсказать, что интересного'
    'есть поблизости!'
)
NUMBER_OF_PLACES_TO_SHOW = 3


async def command_start(message: types.Message):
    try:
        author, created = await User.objects.aget_or_create(
            username=message.from_user.id
        )
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


@func_logger('отправка местоположения', level='info')
async def get_nearest_place(message: types.Message):
    distance = []
    async for place in Place.objects.values_list(
        'name', 'latitude', 'longitude'
    ):
        distance.append(
            (
                place[0],
                haversine(
                    (place[1], place[2]),
                    tuple(message.location.values.values()),
                ),
            )
        )
    nearest_place = await n_max(distance, NUMBER_OF_PLACES_TO_SHOW)
    sended_places = [place[0] for place in nearest_place]
    place_to_send = await Place.objects.aget(name=sended_places[0])
    await send_message(bot, message, 'типа сообщение', reply_markup=kb_client)
    await bot.send_location(
        message.from_user.id, place_to_send.latitude, place_to_send.longitude
    )


@func_logger('вывод всех заведений', level='info')
async def places_all(message: types.Message):
    await sqllite_db.sql_data_base(message)


@func_logger('вывод сообщения о боте', level='info')
async def about_bot(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        'Бот для обмена опыта о посещении различных заведений',
    )


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(
        command_start,
        commands=['start', 'help', 'старт'],
    )
    disp.register_message_handler(
        about_bot,
        commands=[
            'о_боте',
        ],
    )
    disp.register_message_handler(places_all, commands=['место'])
    disp.register_message_handler(
        get_nearest_place, commands=['Отправить_мое_местоположение']
    )
    disp.register_message_handler(
        get_nearest_place, content_types=['location']
    )
