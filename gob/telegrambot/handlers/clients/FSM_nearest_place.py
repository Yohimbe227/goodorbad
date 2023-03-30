"""
Диалог поиска ближайших мест для отдыха.
"""
from copy import copy

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from telegrambot.costants import NUMBER_OF_PLACES_TO_SHOW, PLACE_TYPES
from telegrambot.creation import bot
from telegrambot.database.sqllite_db import (read_places_coordinates,
                                             search_place_name_in_database)
from telegrambot.decorators import func_logger
from telegrambot.keyboards.client_kb import (get_keyboard, kb_client,
                                             kb_client_location)
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import (n_max, send_message,
                               send_message_with_list_of_places,
                               send_message_with_place_name)


class FSMClientSearchPlace(StatesGroup):
    first = State()
    second = State()
    additional = State()


@func_logger('старт поиска ближайших мест', level='info')
async def start_search_place(message: types.Message) -> None:
    """Dialog start."""
    await FSMClientSearchPlace.first.set()
    await send_message(
        bot,
        message,
        'Уточните свои пожелания',
        reply_markup=get_keyboard(PLACE_TYPES.keys()),
    )


@func_logger('выбираем тип заведения', level='info')
async def search_place_request_location(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Получаем тип заведения."""

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
    """Получаем данные геолокации пользователя."""

    async with state.proxy() as data:
        places_distance = await read_places_coordinates(
            message,
            data['place_type'],
        )
        data['places_distance'] = places_distance
        data['city'] = places_distance[0][0]
        nearest_place = await n_max(
            data['places_distance'],
            NUMBER_OF_PLACES_TO_SHOW,
        )
        sended_places = [place[1] for place in nearest_place]
        data['places'] = sended_places
        place_to_send = await search_place_name_in_database(
            sended_places[0],
            places_distance[0][0],
        )
    await send_message_with_list_of_places(
        message,
        bot,
        NUMBER_OF_PLACES_TO_SHOW,
        nearest_place,
        place_to_send,
    )
    await FSMClientSearchPlace.additional.set()


@func_logger('Получаем следующий город', level='info')
async def search_place_additional(message: types.Message, state: FSMContext):
    """
    Отправка локаций для дополнительных заведений или получение
    дополнительного списка заведений
    """
    async with state.proxy() as data:
        match message.text:
            case 'Второе':
                place_name = data['places'][1]
                place_to_send = await search_place_name_in_database(
                    place_name,
                    data['city'],
                )
                await send_message_with_place_name(
                    bot,
                    message,
                    place_name,
                    place_to_send,
                )
            case 'Третье':
                place_name = data['places'][2]
                place_to_send = await search_place_name_in_database(
                    place_name,
                    data['city'],
                )
                await send_message_with_place_name(
                    bot,
                    message,
                    place_name,
                    place_to_send,
                )
            case 'Больше заведений!':
                places_distance = copy(data['places_distance'])
                [
                    places_distance.remove(element)
                    for element in data['places_distance']
                    if element[1] in data['places']
                ]
                data['places_distance'] = places_distance
                nearest_place = await n_max(
                    data['places_distance'],
                    NUMBER_OF_PLACES_TO_SHOW,
                )
                sended_places = [place[1] for place in nearest_place]
                data['places'] = sended_places
                place_to_send = await search_place_name_in_database(
                    sended_places[0],
                    places_distance[0][0],
                )
                len_place_to_send = len(sended_places)
                if (
                    place_to_send
                    and len_place_to_send < NUMBER_OF_PLACES_TO_SHOW
                ):
                    await send_message(
                        bot,
                        message,
                        'Это последние :(',
                        reply_markup=kb_client,
                    )
                    await send_message_with_list_of_places(
                        message,
                        bot,
                        len_place_to_send,
                        nearest_place,
                        place_to_send,
                    )
                    await state.finish()
                elif not place_to_send:
                    await send_message(
                        bot,
                        message,
                        'Больше нет заведений по Вашему запросу :(',
                        reply_markup=kb_client,
                    )
                    await state.finish()
                else:
                    await send_message_with_list_of_places(
                        message,
                        bot,
                        NUMBER_OF_PLACES_TO_SHOW,
                        nearest_place,
                        place_to_send,
                    )


def register_handlers_nearest_place(disp: Dispatcher):
    """Handlers registrations."""

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
    disp.register_message_handler(
        search_place_additional,
        IsCurseMessage(),
        state=FSMClientSearchPlace.additional,
    )
