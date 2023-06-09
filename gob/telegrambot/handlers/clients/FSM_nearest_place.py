"""
Диалог поиска ближайших мест для отдыха.
"""
from copy import copy

import requests
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from telegrambot.costants import (
    GEO_ENDPOINT,
    KEYBOARD_ADDITIONAL,
    NUMBER_OF_PLACES_TO_SHOW,
    PLACE_TYPES,
    YA_GEO_TOKEN,
)
from telegrambot.creation import bot
from telegrambot.database.sqllite_db import (
    read_places_coordinates,
    search_place_name_in_database,
)
from telegrambot.decorators import func_logger
from telegrambot.exceptions import HTTPError
from telegrambot.keyboards.client_kb import (
    get_keyboard,
    kb_client,
    kb_client_location,
    kb_place_client_next,
)
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import (
    n_max,
    send_message,
    send_message_with_list_of_places,
    send_message_with_place_name,
)


class FSMClientSearchPlace(StatesGroup):
    first = State()
    second = State()
    additional = State()


@func_logger('Старт поиска ближайших мест', level='info')
async def start_search_place(message: types.Message) -> None:
    """Dialog start."""
    await FSMClientSearchPlace.first.set()
    await send_message(
        bot,
        message,
        'Уточните свои пожелания',
        reply_markup=get_keyboard(PLACE_TYPES.keys()),
    )


@func_logger('Выбираем тип заведения', level='info')
async def search_place_request_location(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Получаем тип заведения."""

    async with state.proxy() as data:
        if message.text.lower() in PLACE_TYPES:
            data['category'] = message.text.lower()
            await send_message(
                bot,
                message,
                'Отправьте свою локацию, чтобы мы могли подобрать ближайшие заведения'
                ' или напишите свой приблизительный адресс',
                reply_markup=kb_client_location,
            )
            await FSMClientSearchPlace.second.set()
        else:
            await send_message(
                bot,
                message,
                'Такого типа заведения в нашей базе нет,'
                ' воспользуйтесь вариантами с клавиатуры!',
                reply_markup=get_keyboard(PLACE_TYPES.keys()),
            )


@func_logger('Получаем данные локации', level='info')
async def search_place_done(message: types.Message, state: FSMContext):
    """Получаем данные геолокации пользователя."""
    if message.text:
        try:
            response = requests.get(
                GEO_ENDPOINT,
                params={
                    'geocode': message.text,
                    'apikey': YA_GEO_TOKEN,
                    'format': 'json',
                },
            )
        except requests.RequestException as error:
            raise HTTPError(f"Эндпоинт {GEO_ENDPOINT}' не доступен") from error
        try:
            location = response.json()['response']['GeoObjectCollection'][
                'featureMember'
            ][0]['GeoObject']['Point']['pos'].split(' ')
            location = location[::-1]
        except (KeyError, IndexError):
            await send_message(
                bot,
                message,
                f'Проверьте введенный адресс <b>{message.text}</b>, '
                f'а то не находится ничего!',
                reply_markup=kb_client_location,
            )
            location = None

    if message.location:
        location = list(dict(message.location).values())

    if message.location or location:
        async with state.proxy() as data:
            if places_distance := await read_places_coordinates(
                location,
                data['category'],
            ):
                data['places_distance'] = places_distance
                nearest_place = await n_max(
                    data['places_distance'],
                    NUMBER_OF_PLACES_TO_SHOW,
                )
                data['city'] = nearest_place[0][0]
                sended_places = [place[1] for place in nearest_place]
                data['places'] = sended_places
                place_to_send = await search_place_name_in_database(
                    sended_places[0],
                    data['city'],
                )
                await send_message_with_list_of_places(
                    message,
                    bot,
                    NUMBER_OF_PLACES_TO_SHOW,
                    nearest_place,
                    place_to_send,
                )
                await FSMClientSearchPlace.additional.set()
                if data['city'] == 'Петрозаводск':
                    await send_message(
                        bot,
                        message,
                        'Пасхалка для лучшего ревьюера Анюты Агаренко :)',
                    )

            else:
                await send_message(
                    bot,
                    message,
                    'Тут ничего нет, совсем.',
                    reply_markup=kb_client_location,
                )
    if message.content_type not in ('text', 'location'):
        await send_message(
            bot,
            message,
            'Сюда стоит слать только адресс или свои '
            'координаты по кнопочке с клавиатуры',
        )
        await message.delete()


@func_logger('Получаем следующее заведение', level='info')
async def search_place_additional(message: types.Message, state: FSMContext):
    """
    Отправка локаций для дополнительных заведений или получение
    дополнительного списка заведений
    """
    if message.text not in KEYBOARD_ADDITIONAL:
        await send_message(
            bot,
            message,
            'Не нужно сюда ничего печатать, жмите кнопочки на клавиатуре!',
            reply_markup=kb_place_client_next,
        )
    else:
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
                    len_place_to_send = len(places_distance)
                    if places_distance:
                        nearest_place = await n_max(
                            data['places_distance'],
                            NUMBER_OF_PLACES_TO_SHOW,
                        )
                        sended_places = [place[1] for place in nearest_place]
                        data['places'] = sended_places
                        place_to_send = await search_place_name_in_database(
                            sended_places[0],
                            nearest_place[0][0],
                        )
                    if (
                        places_distance
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
                            reply_markup=kb_client,
                        )
                        await state.finish()
                    elif not places_distance:
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
        commands=[
            'ближайшее_место_для...',
            'NextPlace',
        ],
    )
    disp.register_message_handler(
        search_place_request_location,
        IsCurseMessage(),
        state=FSMClientSearchPlace.first,
    )
    disp.register_message_handler(
        search_place_done,
        IsCurseMessage(),
        state=FSMClientSearchPlace.second,
        content_types=[
            'any',
        ],
    )
    disp.register_message_handler(
        search_place_additional,
        IsCurseMessage(),
        state=FSMClientSearchPlace.additional,
    )
