from aiogram.types import KeyboardButton

from administration.models import Place, Review, User
from aiogram import types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import IDFilter, Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from django.core.exceptions import MultipleObjectsReturned
from django.db import IntegrityError
from haversine import haversine
from telegrambot.creation import ID, bot
from telegrambot.database import sqllite_db
from telegrambot.database.sqllite_db import (add_review_in_database,
                                             search_place_name_in_database,
                                             read_review_from_database)
from telegrambot.decorators import func_logger
from telegrambot.exceptions import UnknownError
from telegrambot.handlers.admin import cancel_handler
from telegrambot.keyboards.city_kb import kb_city
from telegrambot.keyboards.client_kb import (kb_client, kb_client_with_places,
                                             kb_start,
                                             get_keyboard, NUMBER_OF_COLUMNS_KB)
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import n_max, send_message

START_MESSAGE = (
    'Добро пожаловать {username}. Для удобства нажмите кнопочку'
    '`Отправить мое местоположение`. Тогда мы сможем подсказать, что интересного'
    'есть поблизости!'
)
NUMBER_OF_PLACES_TO_SHOW = 3
MAX_QUANTITY_OF_PLACES = 12


class FSMClientReview(StatesGroup):

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


@func_logger('старт добавления отзыва', level='info')
async def start_add_review(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['mode'] = 'write'
    await FSMClientReview.city.set()
    await send_message(
        bot, message, 'Введите Ваш город!', reply_markup=kb_city
    )


@func_logger('добавляется город...', level='info')
async def add_city(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['city'] = message.text
    await FSMClientReview.name.set()
    await message.reply('Введите название заведения')


@func_logger('добавляется название заведения', level='info')
async def add_place_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        places = await search_place_name_in_database(data['name'])

        match len(places):
            case 0:
                await send_message(
                    bot,
                    message,
                    f'Мы не нашли такого заведения {data["name"]}.'
                    f' Может что-то не так с названием?',
                )
            case 1:
                # print(data, data['mode'])
                if data['mode'] == 'write':
                    await send_message(
                        bot,
                        message,
                        'Введите Ваш отзыв',
                        reply_markup=kb_client,
                    )
                    data['places'] = places[0]
                    await FSMClientReview.review.set()
                else:
                    reviews = await read_review_from_database(places[0])
                    reviews_text = [review.text async for review in reviews]
                    await send_message(
                        bot,
                        message,
                        '\n'.join(reviews_text),
                        reply_markup=kb_client,
                    )
                    # print(read_review_from_database(places[0]))
                    await state.finish()

            case _:
                buttons = [KeyboardButton(place.name) for place in places[:MAX_QUANTITY_OF_PLACES]]

                await send_message(
                    bot,
                    message,
                    f'Слишком общий запрос {data["name"]}. Уточните!'
                    f'\nна клавиатуре самые похожие названия, но Вы можете ввести свое!',
                    reply_markup=get_keyboard(buttons),
                )


@func_logger('добавляется текст отзыва', level='info')
async def add_place_review(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['review'] = message.text
    await add_review_in_database(data['places'], data['review'])
    await send_message(
        bot,
        message,
        'Ваш отзыв успешно сохранен',
        reply_markup=kb_client,
    )
    await state.finish()


@func_logger('старт просмотра отзывов', level='info')
async def start_read_review(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['mode'] = 'read'
    await FSMClientReview.city.set()
    await send_message(
        bot, message, 'Введите город!', reply_markup=kb_city
    )


# @func_logger('считывается текст отзыва', level='info')
# async def read_place_review(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['review'] = message.text
#     await read_review_from_database(data['places'])
#     await send_message(
#         bot,
#         message,
#         'Ваш отзыв успешно сохранен',
#         reply_markup=kb_client,
#     )
#     await state.finish()


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(
        command_start,
        commands=[
            'start',
            'help',
            'старт'
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
        get_nearest_place, commands=['Отправить_мое_местоположение']
    )
    disp.register_message_handler(
        get_nearest_place, content_types=['location']
    )
    disp.register_message_handler(
        start_add_review,
        IsCurseMessage(),
        state=None,
        commands=['добавить_отзыв', ],
    )
    disp.register_message_handler(
        cancel_handler, Text(equals='отмена', ignore_case=True), state='*'
    )
    disp.register_message_handler(
        add_city, IsCurseMessage(), state=FSMClientReview.city
    )
    disp.register_message_handler(
        add_place_name, IsCurseMessage(), state=FSMClientReview.name,
    )
    disp.register_message_handler(
        add_place_review, IsCurseMessage(), state=FSMClientReview.review
    )

    disp.register_message_handler(
        start_read_review, IsCurseMessage(), state=None, commands=['узнать_отзывы']
    )

    # disp.register_message_handler(
    #     read_place_review, IsCurseMessage(), state=FSMClientReview.name
    # )
