from aiogram.dispatcher.filters import IDFilter, Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from administration.models import Place, User
from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from django.contrib.auth import get_user, get_user_model
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from haversine import haversine
from telegrambot.creation import bot, ID
from telegrambot.database import sqllite_db
from telegrambot.database.sqllite_db import add_review_in_database
from telegrambot.decorators import func_logger
from telegrambot.exceptions import UnknownError
from telegrambot.handlers.admin import cancel_handler
from telegrambot.keyboards.city_kb import kb_city
from telegrambot.keyboards.client_kb import kb_client, kb_start, \
    kb_client_with_places
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import send_message

START_MESSAGE = (
    'Добро пожаловать {username}. Для удобства нажмите кнопочку'
    '`Отправить мое местоположение`. Тогда мы сможем подсказать, что интересного'
    'есть поблизости!'
)


class FSMAdmin(StatesGroup):
    """Class of states."""

    city = State()
    name = State()
    review = State()


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
async def get_location(message: types.Message):
    # print(list(message.location.values.values()))
    distance = []
    async for place in Place.objects.all().select_related():
        distance.append(
            (
                place.name,
                haversine(
                    (place.latitude, place.longitude),
                    tuple(message.location.values.values()),
                ),
            )
        )
    nearest_place = sorted(distance, key=lambda place: place[1])

    try:
        await send_message(
            bot, message, nearest_place[0:2], reply_markup=kb_client
        )
    except Exception as error:
        print('Непонятная ошибка')


@func_logger('вывод всех заведений', level='info')
async def places_all(message: types.Message):
    await sqllite_db.sql_data_base(message)


@func_logger('вывод сообщения о боте', level='info')
async def about_bot(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        'Бот для обмена опыта о посещении различных заведений',
    )


@func_logger('старт добавления отзыва', level='info')
async def start_review(message: types.Message):

    await FSMAdmin.city.set()
    await send_message(
        bot,
        message,
        'Введите Ваш город!',
        reply_markup=kb_city
    )


@func_logger('добавляется город...', level='info')
async def add_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text
    await FSMAdmin.next()
    await message.reply('Введите название заведения')


@func_logger('добавлялся название заведения', level='info')
async def add_place_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    await message.reply('Введите Ваш отзыв')


@func_logger('добавлялся текст отзыва', level='info')
async def add_place_review(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['review'] = message.text
    await add_review_in_database(state)
    async with state.proxy() as data:
        await send_message(bot, message, str(data._data)[1:-1])
        await send_message(
            bot, message, 'Добавление нового заведения закончено', reply_markup=kb_client
        )
    await state.finish()


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(
        command_start,
        commands=[
            'start',
            'help',
        ],
    )
    disp.register_message_handler(
        about_bot,
        commands=[
            'о_боте',
        ],
    )
    disp.register_message_handler(places_all, commands=['место'])
    disp.register_message_handler(
        get_location, commands=['отправить_мое_местоположение']
    )
    disp.register_message_handler(get_location, content_types=['location'])
    disp.register_message_handler(
        start_review,
        IDFilter(user_id=ID),
        commands=[
            'добавить_отзыв',
        ],
        state=None,
    )
    # disp.register_message_handler(cancel_handler, state='*', commands='Отмена')
    disp.register_message_handler(
        cancel_handler, Text(equals='отмена', ignore_case=True), state='*'
    )
    disp.register_message_handler(
        add_city, IsCurseMessage(), state=FSMAdmin.city
    )
    disp.register_message_handler(
        add_place_name, IsCurseMessage(), state=FSMAdmin.name
    )
    disp.register_message_handler(
        add_place_review, IsCurseMessage(), state=FSMAdmin.review
    )
