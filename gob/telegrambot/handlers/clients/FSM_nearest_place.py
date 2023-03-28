from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from administration.models import Place
from telegrambot.costants import PLACE_TYPES
from telegrambot.creation import bot
from telegrambot.database.sqllite_db import read_places_coordinates
from telegrambot.decorators import func_logger
from telegrambot.handlers.clients.basic import NUMBER_OF_PLACES_TO_SHOW
from telegrambot.keyboards.client_kb import (get_keyboard, kb_client,
                                             kb_client_location)
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import n_max, send_message

M_IN_KM = 1000  # 1000 to become the distance in meter
BUTTONS_PLACE_TYPE = (
    'Бар',
    'Ресторан',
    'Кафе',
    'Пиццерия',
    'Фастфуд',
    'Суши бар',
    'Кофейня',
    'Караоке',
)


class FSMClientSearchPlace(StatesGroup):
    first = State()
    second = State()


@func_logger('старт поиска ближайших мест', level='info')
async def start_search_place(message: types.Message):
    await FSMClientSearchPlace.first.set()
    await send_message(
        bot,
        message,
        'Уточните свои пожелания',
        reply_markup=get_keyboard(PLACE_TYPES.keys()),
    )


@func_logger('выбираем тип заведения', level='info')
async def search_place_request_location(
    message: types.Message, state: FSMContext
):
    async with state.proxy() as data:
        data['place_type'] = message.text
    await send_message(
        bot,
        message,
        'Отправьте свою локацию, чтобы мы могли подобрать ближайшие заведения',
        reply_markup=kb_client_location,
    )
    await FSMClientSearchPlace.second.set()


@func_logger('получаем данные локации', level='info')
async def search_place_done(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        distance = await read_places_coordinates(message, data['place_type'])
        print(distance)
    nearest_place = await n_max(distance, NUMBER_OF_PLACES_TO_SHOW)
    sended_places = [place[0] for place in nearest_place]
    place_to_send = await Place.objects.aget(name=sended_places[0])
    await send_message(
        bot,
        message,
        f'Вот {NUMBER_OF_PLACES_TO_SHOW} заведения и первое из них на <b>карте</b>: \n-> '
        + '\n-> '.join(
            [
                str(round(distance_ * M_IN_KM)) + ' м.: <b>' + place + '</b>'
                for place, distance_ in nearest_place
            ]
        ),
        reply_markup=kb_client,
    )
    await bot.send_location(
        message.from_user.id, place_to_send.latitude, place_to_send.longitude
    )
    await state.finish()


def register_handlers_nearest_place(disp: Dispatcher):
    disp.register_message_handler(
        start_search_place,
        IsCurseMessage(),
        state=None,
        commands=['ближайшее_место_для...'],
    )
    disp.register_message_handler(
        search_place_request_location,
        IsCurseMessage(),
        state=FSMClientSearchPlace.first,
    )
    disp.register_message_handler(
        search_place_done,
        state=FSMClientSearchPlace.second,
        content_types=[
            'location',
        ],
    )
