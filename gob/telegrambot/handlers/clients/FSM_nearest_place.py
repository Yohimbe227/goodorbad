"""
Диалог поиска ближайших мест для отдыха.
"""
from copy import copy
from logging.handlers import RotatingFileHandler

import requests
from aiogram import Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from administration.models import Place
from telegrambot.costants import (
    GEO_ENDPOINT,
    KEYBOARD_ADDITIONAL,
    LOCATION_REQUEST,
    NO_PLACE_PRESENTED,
    NUMBER_OF_PLACES_TO_SHOW,
    PLACE_TYPES,
    YA_GEO_TOKEN,
    WARNING_LOCATION,
    HERE_IS_NOTHING_MESSAGE,
    NO_TYPING_HERE_MESSAGE,
    ITS_LAST_PLACES_MESSAGE,
    NO_MORE_PLACES_MESSAGE,
)
from telegrambot.creation import bot
from telegrambot.database.database_functions import (
    city_name,
    read_places_coordinates,
)
from telegrambot.decorators import func_logger
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
    first = State()
    second = State()
    additional = State()


@func_logger("Старт поиска ближайших мест", level="info")
async def start_search_place(
    message: types.Message, state: FSMContext
) -> None:
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
            LOCATION_REQUEST,
            reply_markup=kb_client_location,
        )
        await state.set_state(FSMClientSearchPlace.second)
    else:
        await send_message(
            bot,
            message,
            NO_PLACE_PRESENTED,
            reply_markup=get_keyboard(PLACE_TYPES.keys()),
        )


async def get_user_coordinates(
    message: types.Message,
) -> tuple[float, float] | None:
    """
    Get user coordinates from the message.

    Args:
        message: Telegram message object.

    Returns:
        Tuple of latitude and longitude coordinates if successful,
        None otherwise.
    """
    if message.content_type == "location":
        return tuple(dict(message.location).values())[:2]
    elif message.content_type == "text":
        try:
            with requests.get(
                GEO_ENDPOINT,
                params={
                    "geocode": message.text,
                    "apikey": YA_GEO_TOKEN,
                    "format": "json",
                },
            ) as response:
                response.raise_for_status()
                data = response.json()["response"]["GeoObjectCollection"][
                    "featureMember"
                ][0]["GeoObject"]["Point"]["pos"]
                return tuple(map(float, data.split(" ")))
        except (requests.RequestException, KeyError, IndexError) as e:
            logger.error(f"Error getting user coordinates: {e}")
            await send_message(
                message.bot,
                message,
                f"Проверьте введенный адрес <b>{message.text}</b>,"
                f"а то не находится ничего!",
                reply_markup=kb_client_return,
            )
    return None


@func_logger("Получаем данные локации", level="info")
async def search_place_done(message: types.Message, state: FSMContext) -> None:
    """
    Retrieve user's location data and search for nearby places.

    Args:
        message: Telegram message object.
        state: FSM state object.
    """
    user_coordinates = await get_user_coordinates(message)
    if not user_coordinates:
        if message.text == button_return.text:
            await send_message(
                message.bot, message, "", reply_markup=kb_client
            )
        else:
            await send_message(
                message.bot,
                message,
                WARNING_LOCATION,
            )
            await message.delete()
        return

    data = await state.get_data()
    places_with_distances = await read_places_coordinates(
        user_coordinates, data["category"]
    )
    if places_with_distances:
        await state.update_data(places_with_distances=places_with_distances)
        nearest_places = await n_min(
            places_with_distances, NUMBER_OF_PLACES_TO_SHOW
        )
        await state.update_data(nearest_places=nearest_places)
        await state.update_data(city=await city_name(nearest_places[0][0]))
        await send_message_with_list_of_places(
            message, message.bot, NUMBER_OF_PLACES_TO_SHOW, nearest_places
        )
        await state.set_state(FSMClientSearchPlace.additional)
    else:
        await send_message(
            message.bot,
            message,
            HERE_IS_NOTHING_MESSAGE,
            reply_markup=kb_client_return,
        )


async def send_place_location(message: types.Message, place: Place) -> None:
    """
    Send the location of a place to the user.

    Args:
        message: Telegram message object.
        place: Tuple containing the place object and its distance.
    """
    await send_message(
        message.bot, message, place.name, reply_markup=kb_place_client_next
    )
    await message.bot.send_location(
        message.from_user.id, float(place.latitude), float(place.longitude)
    )


@func_logger("Получаем следующее заведение", level="info")
async def search_place_additional(
    message: types.Message, state: FSMContext
) -> None:
    """
    Send locations for additional places and receive additional list of locations.
    """
    if message.text not in KEYBOARD_ADDITIONAL:
        await send_message(
            message.bot,
            message,
            NO_TYPING_HERE_MESSAGE,
            reply_markup=kb_place_client_next,
        )
        return

    data: dict = await state.get_data()
    nearest_places: list[tuple[Place, float]] = data["nearest_places"]

    if message.text == "Второе":
        await send_place_location(message, nearest_places[1][0])
    elif message.text == "Третье":
        await send_place_location(message, nearest_places[2][0])
    elif message.text == "Больше заведений!":
        places_with_distances = copy(data["places_with_distances"])
        places_with_distances = [
            place
            for place in places_with_distances
            if place not in nearest_places
        ]
        await state.update_data(places_with_distances=places_with_distances)

        len_places_to_send = len(places_with_distances)
        nearest_places = await n_min(
            places_with_distances, NUMBER_OF_PLACES_TO_SHOW
        )

        if places_with_distances:
            await state.update_data(nearest_places=nearest_places)

        if (
            places_with_distances
            and len_places_to_send < NUMBER_OF_PLACES_TO_SHOW
        ):
            await send_message(
                message.bot,
                message,
                ITS_LAST_PLACES_MESSAGE,
                reply_markup=kb_client,
            )
            await send_message_with_list_of_places(
                message,
                message.bot,
                len_places_to_send,
                nearest_places,
                reply_markup=kb_client,
            )
            await state.clear()
        elif not places_with_distances:
            await send_message(
                message.bot,
                message,
                NO_MORE_PLACES_MESSAGE,
                reply_markup=kb_client,
            )
            await state.clear()
        else:
            await send_message_with_list_of_places(
                message,
                message.bot,
                NUMBER_OF_PLACES_TO_SHOW,
                nearest_places,
            )

#
# @func_logger("Получаем следующее заведение", level="info")
# async def search_place_additional(message: types.Message, state: FSMContext):
#     """
#     Sending locations for additional places and receiving
#     additional list of locations.
#
#     """
#     if message.text not in KEYBOARD_ADDITIONAL:
#         await send_message(
#             bot,
#             message,
#             NO_TYPING_HERE_MESSAGE,
#             reply_markup=kb_place_client_next,
#         )
#     else:
#         data = await state.get_data()
#         match message.text:
#             case "Второе":
#                 place_name = data["nearest_places"][1][0].name
#                 await send_message(
#                     bot,
#                     message,
#                     place_name,
#                     reply_markup=kb_place_client_next,
#                 )
#                 await bot.send_location(
#                     message.from_user.id,
#                     data["nearest_places"][1][0].latitude,
#                     data["nearest_places"][1][0].longitude,
#                 )
#             case "Третье":
#                 place_name = data["nearest_places"][2][0].name
#                 await send_message(
#                     bot,
#                     message,
#                     place_name,
#                     reply_markup=kb_place_client_next,
#                 )
#                 await bot.send_location(
#                     message.from_user.id,
#                     data["nearest_places"][2][0].latitude,
#                     data["nearest_places"][2][0].longitude,
#                 )
#
#             case "Больше заведений!":
#                 places_with_distances = copy(data["places_with_distances"])
#                 [
#                     places_with_distances.remove(element)
#                     for element in data["places_with_distances"]
#                     if element in [place for place in data["nearest_places"]]
#                 ]
#                 await state.update_data(
#                     places_with_distances=places_with_distances
#                 )
#                 len_place_to_send = len(places_with_distances)
#                 nearest_places = await n_min(
#                     places_with_distances,
#                     NUMBER_OF_PLACES_TO_SHOW,
#                 )
#                 if places_with_distances:
#                     await state.update_data(nearest_places=nearest_places)
#                 if (
#                     places_with_distances
#                     and len_place_to_send < NUMBER_OF_PLACES_TO_SHOW
#                 ):
#                     await send_message(
#                         bot,
#                         message,
#                         ITS_LAST_PLACES_MESSAGE,
#                         reply_markup=kb_client,
#                     )
#                     await send_message_with_list_of_places(
#                         message,
#                         bot,
#                         len_place_to_send,
#                         data["nearest_places"],
#                         reply_markup=kb_client,
#                     )
#                     await state.clear()
#                 elif not places_with_distances:
#                     await send_message(
#                         bot,
#                         message,
#                         NO_MORE_PLACES_MESSAGE,
#                         reply_markup=kb_client,
#                     )
#                     await state.clear()
#                 else:
#                     await send_message_with_list_of_places(
#                         message,
#                         bot,
#                         NUMBER_OF_PLACES_TO_SHOW,
#                         nearest_places,
#                     )
#

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
