"""
Диалог поиска ближайших мест для отдыха.
"""
from copy import copy
from logging.handlers import RotatingFileHandler

import requests
from aiogram import Dispatcher, types, F

# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Text
# from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from telegrambot.costants import (
    GEO_ENDPOINT,
    KEYBOARD_ADDITIONAL,
    NUMBER_OF_PLACES_TO_SHOW,
    PLACE_TYPES,
    YA_GEO_TOKEN,
)
from telegrambot.creation import bot
from telegrambot.database.database_functions import (
    city_name,
    read_places_coordinates,
)
from telegrambot.decorators import func_logger
from telegrambot.exceptions import HTTPError
from telegrambot.keyboards.client_kb import (
    button_return,
    get_keyboard,
    kb_client,
    kb_client_categories,
    kb_client_location,
    kb_client_return,
    kb_place_client_next,
)
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import (
    logging,
    n_min,
    send_message,
    send_message_with_list_of_places,
)

logger = logging.getLogger(
    __name__,
)

handler = RotatingFileHandler(
    "nearest_places.log",
    maxBytes=5000000,
    backupCount=3,
)
logger.addHandler(handler)
logger.setLevel("DEBUG")
formatter = logging.Formatter(
    "%(asctime)s, %(levelname)s, %(message)s, %(funcName)s",
)
handler.setFormatter(formatter)


class FSMClientSearchPlace(StatesGroup):
    flag = State()
    first = State()
    second = State()
    additional = State()


@func_logger("Старт поиска ближайших мест", level="info")
async def start_search_place(message: types.Message, state: FSMContext) -> None:
    """Start the nearest place search.

    Args:
        state: Current state.
        message: Object `message` telegram with everyone info.

    """
    await state.set_state(FSMClientSearchPlace.first)
    await send_message(
        bot,
        message,
        "Уточните свои пожелания",
        reply_markup=kb_client_categories,
    )


@func_logger("Выбираем тип заведения", level="info")
async def search_place_request_location(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Retrieving place category.

    The selected category is matched with the real categories in the database
    by the PLACE_TYPES dictionary.

    Args:
        message: Object `message` telegram with everyone info.
        state: State object that stores the current state.

    """
    if message.text.lower() in PLACE_TYPES:
        await state.update_data(category=message.text)
        await send_message(
            bot,
            message,
            "Отправьте свою локацию, чтобы мы могли подобрать ближайшие "
            "заведения или напишите свой приблизительный адресс, "
            "содержащий город, улицу и номер дома, формат не важен.",
            reply_markup=kb_client_location,
        )
        await state.set_state(FSMClientSearchPlace.second)
    else:
        await send_message(
            bot,
            message,
            "Такого типа заведения в нашей базе нет,"
            " воспользуйтесь вариантами с клавиатуры!",
            reply_markup=get_keyboard(PLACE_TYPES.keys()),
        )


@func_logger("Получаем данные локации", level="info")
async def search_place_done(message: types.Message, state: FSMContext) -> None:
    """Retrieving user geolocation data.

    The location data can come in the form of a telegram object or as an
    address, entered by the user.

    Args:
        message: Object `message` telegram with everyone info.
        state: State object that stores the current state.

    Raises:
        HTTPError: If endpoint is not available.

    """
    if message.text:
        try:
            response = requests.get(
                GEO_ENDPOINT,
                params={
                    "geocode": message.text,
                    "apikey": YA_GEO_TOKEN,
                    "format": "json",
                },
            )
        except requests.RequestException as error:
            raise HTTPError(f"Эндпоинт {GEO_ENDPOINT}' не доступен") from error
        try:
            location = response.json()["response"]["GeoObjectCollection"][
                "featureMember"
            ][0]["GeoObject"]["Point"]["pos"].split(" ")
            location = list(map(float, location[::-1]))
        except (KeyError, IndexError):
            await send_message(
                bot,
                message,
                f"Проверьте введенный адресс <b>{message.text}</b>, "
                f"а то не находится ничего!",
                reply_markup=kb_client_return,
            )
            location = None

    if message.location:
        location = list(dict(message.location).values())[:2]
    if message.location or location:
        data = await state.get_data()
        if places_distance := await read_places_coordinates(
            location,
            data["category"],
        ):
            await state.update_data(places_distance=places_distance)
            nearest_places = await n_min(
                places_distance,
                NUMBER_OF_PLACES_TO_SHOW,
            )
            await state.update_data(nearest_places=nearest_places)
            await state.update_data(city=await city_name(nearest_places[0][0]))
            await send_message_with_list_of_places(
                message,
                bot,
                NUMBER_OF_PLACES_TO_SHOW,
                nearest_places,
            )
            await state.set_state(FSMClientSearchPlace.additional)
        else:
            if message.text == button_return.text:
                await send_message(
                    bot,
                    message,
                    "",
                    reply_markup=kb_client,
                )
            await send_message(
                bot,
                message,
                "Тут ничего нет, совсем. Или Ваш город не поддерживается",
                reply_markup=kb_client_return,
            )
    if message.content_type not in ("text", "location"):
        await send_message(
            bot,
            message,
            "Сюда стоит слать только адресс или свои "
            "координаты по кнопочке с клавиатуры",
        )
        await message.delete()


@func_logger("Получаем следующее заведение", level="info")
async def search_place_additional(message: types.Message, state: FSMContext):
    """
    Sending locations for additional places and receiving
    additional list of locations.

    """
    if message.text not in KEYBOARD_ADDITIONAL:
        await send_message(
            bot,
            message,
            "Не нужно сюда ничего печатать, жмите кнопочки на клавиатуре!",
            reply_markup=kb_place_client_next,
        )
    else:
        data = await state.get_data()
        match message.text:
            case "Второе":
                place_name = data["nearest_places"][1][0].name
                await send_message(
                    bot,
                    message,
                    place_name,
                    reply_markup=kb_place_client_next,
                )
                await bot.send_location(
                    message.from_user.id,
                    data["nearest_places"][1][0].latitude,
                    data["nearest_places"][1][0].longitude,
                )
            case "Третье":
                place_name = data["nearest_places"][2][0].name
                await send_message(
                    bot,
                    message,
                    place_name,
                    reply_markup=kb_place_client_next,
                )
                await bot.send_location(
                    message.from_user.id,
                    data["nearest_places"][2][0].latitude,
                    data["nearest_places"][2][0].longitude,
                )

            case "Больше заведений!":
                places_distance = copy(data["places_distance"])
                [
                    places_distance.remove(element)
                    for element in data["places_distance"]
                    if element in [place for place in data["nearest_places"]]
                ]
                await state.update_data(places_distance=places_distance)
                len_place_to_send = len(places_distance)
                if places_distance:
                    await state.update_data(
                        nearest_places=await n_min(
                            data["places_distance"],
                            NUMBER_OF_PLACES_TO_SHOW,
                        )
                    )
                if places_distance and len_place_to_send < NUMBER_OF_PLACES_TO_SHOW:
                    await send_message(
                        bot,
                        message,
                        "Это последние :(",
                        reply_markup=kb_client,
                    )
                    await send_message_with_list_of_places(
                        message,
                        bot,
                        len_place_to_send,
                        data["nearest_places"],
                        reply_markup=kb_client,
                    )
                    await state.clear()
                elif not places_distance:
                    await send_message(
                        bot,
                        message,
                        "Больше нет заведений по Вашему запросу :(",
                        reply_markup=kb_client,
                    )
                    await state.clear()
                else:
                    await send_message_with_list_of_places(
                        message,
                        bot,
                        NUMBER_OF_PLACES_TO_SHOW,
                        data["nearest_places"],
                    )


async def register_handlers_nearest_place(dp: Dispatcher):
    """Handlers registrations."""
    dp.message.filter(IsCurseMessage())
    dp.message.register(
        start_search_place,
        F.text.in_({"Ближайшее место для...", "/next_place"}),
    )
    dp.message.register(
        search_place_request_location,
        FSMClientSearchPlace.first,
    )
    dp.message.register(
        search_place_done,
        FSMClientSearchPlace.second,
    )
    dp.message.register(
        search_place_additional,
        FSMClientSearchPlace.additional,
    )
