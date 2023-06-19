"""
Dialog for addind and reading reviews.
The FSM work on `write` and `read` mode. It's controls by `mode` key
in `data` dictionary
"""
import logging
from logging.handlers import RotatingFileHandler

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from telegrambot.costants import MAX_QUANTITY_OF_PLACES_ON_KB
from telegrambot.creation import bot
from telegrambot.database.database_functions import (
    add_review_in_database,
    get_cities,
    read_review_from_database,
    search_place_name_in_database,
)
from telegrambot.decorators import func_logger
from telegrambot.handlers.admin import cancel_handler
from telegrambot.keyboards.city_kb import kb_city
from telegrambot.keyboards.client_kb import get_keyboard, kb_client
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import send_message


logger = logging.getLogger(__name__)

handler = RotatingFileHandler('review.log', maxBytes=5000000, backupCount=3)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s, %(funcName)s',
)
handler.setFormatter(formatter)


class FSMClientReview(StatesGroup):
    city = State()
    name = State()
    review = State()


@func_logger('Старт добавления отзыва', level='info')
async def start_add_review(message: types.Message, state: FSMContext) -> None:
    """Dialog start."""

    async with state.proxy() as data:
        data['mode'] = 'write'
    await FSMClientReview.city.set()
    await send_message(
        bot,
        message,
        'Введите Ваш город!',
        reply_markup=kb_city,
    )


@func_logger('Добавляется город...', level='info')
async def add_city(message: types.Message, state: FSMContext) -> None:
    """Get the name of the user's city."""

    if message.text in await get_cities():
        async with state.proxy() as data:
            data['city'] = message.text
        await FSMClientReview.name.set()
        await message.reply('Введите название заведения')
    else:
        await send_message(
            bot,
            message,
            f'Город <b>{message.text}</b> пока не поддерживается',
        )


@func_logger('Вводится название заведения', level='info')
async def add_place_name(message: types.Message, state: FSMContext) -> None:
    """Get the name of the place."""

    async with state.proxy() as data:
        data['name'] = message.text
        places = await search_place_name_in_database(
            data['name'],
            data['city'],
        )
        match len(places):
            case 0:
                await send_message(
                    bot,
                    message,
                    f'Мы не нашли такого заведения {data["name"]}.'
                    f' Может что-то не так с названием?',
                )
            case 1:
                if data['mode'] == 'write':
                    await send_message(
                        bot,
                        message,
                        f'Введите Ваш отзыв на <b>"{places[0]}"</b>',
                        reply_markup=kb_client,
                    )
                    data['places'] = places[0]
                    await FSMClientReview.review.set()
                else:
                    await send_message(
                        bot,
                        message,
                        await read_review_from_database(places[0], message),
                        reply_markup=kb_client,
                    )
                    await state.finish()

            case _:
                buttons = [
                    place.name
                    for place in places[:MAX_QUANTITY_OF_PLACES_ON_KB]
                ]
                await send_message(
                    bot,
                    message,
                    f'Слишком общий запрос "{data["name"]}". Уточните!'
                    f'\nна клавиатуре самые похожие названия, но Вы можете '
                    f'ввести свое!',
                    reply_markup=get_keyboard(buttons),
                )


@func_logger('Добавляется текст отзыва', level='info')
async def add_place_review(message: types.Message, state: FSMContext):
    """Получаем отзыв и сохраняем его в базу данных."""

    async with state.proxy() as data:
        data['review'] = message.text
    await add_review_in_database(data['places'], data['review'], message)
    await send_message(
        bot,
        message,
        'Ваш отзыв успешно сохранен',
        reply_markup=kb_client,
    )
    await state.finish()


@func_logger('Старт просмотра отзывов', level='info')
async def start_read_review(message: types.Message, state: FSMContext):
    """Dialog read reviews start."""
    async with state.proxy() as data:
        data['mode'] = 'read'
    await FSMClientReview.city.set()
    await send_message(bot, message, 'Введите город!', reply_markup=kb_city)


def register_handlers_fsm(disp: Dispatcher):
    """Hadlers register."""

    disp.register_message_handler(
        start_read_review,
        IsCurseMessage(),
        state=None,
        commands=[
            'узнать_отзывы',
        ],
    )
    disp.register_message_handler(
        start_add_review,
        IsCurseMessage(),
        state=None,
        commands=['добавить_отзыв', 'add_reviews'],
    )
    disp.register_message_handler(
        cancel_handler,
        Text(equals='отмена', ignore_case=True),
        state='*',
    )
    disp.register_message_handler(
        add_city,
        IsCurseMessage(),
        state=FSMClientReview.city,
    )
    disp.register_message_handler(
        add_place_name,
        IsCurseMessage(),
        state=FSMClientReview.name,
    )
    disp.register_message_handler(
        add_place_review,
        IsCurseMessage(),
        state=FSMClientReview.review,
    )

    disp.register_message_handler(
        start_read_review,
        IsCurseMessage(),
        state=None,
        commands=['узнать_отзывы', 'reviews'],
    )
