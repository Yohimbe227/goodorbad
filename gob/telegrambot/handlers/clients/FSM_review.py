"""
Dialog for addind and reading reviews.
The FSM work on `write` and `read` mode. It's controls by `mode` key
in `data` dictionary
"""
import logging
from logging.handlers import RotatingFileHandler

from aiogram import Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from telegrambot.costants import (
    MAX_QUANTITY_OF_PLACES_ON_KB,
    NOT_FOUND_PLACE_MESSAGE,
    INPUT_YOUR_MESSAGE,
    TOO_GLOBAL_REQUEST,
)
from telegrambot.creation import bot
from telegrambot.database.database_functions import (
    add_review_in_database,
    get_cities,
    read_review_from_database,
    search_place_name_in_database,
)
from telegrambot.decorators import func_logger
from telegrambot.keyboards.city_kb import kb_city
from telegrambot.keyboards.client_kb import get_keyboard, kb_client
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import send_message

logger = logging.getLogger(__name__)

handler = RotatingFileHandler("review.log", maxBytes=5000000, backupCount=3)
logger.addHandler(handler)
formatter = logging.Formatter(
    "%(asctime)s, %(levelname)s, %(message)s, %(funcName)s",
)
handler.setFormatter(formatter)


class FSMClientReview(StatesGroup):
    city = State()
    name = State()
    review = State()


@func_logger("Старт добавления отзыва", level="info")
async def start_add_review(message: types.Message, state: FSMContext) -> None:
    """Dialog start."""

    await state.update_data(mode="write")
    await state.set_state(FSMClientReview.city)
    await send_message(
        bot,
        message,
        "Введите Ваш город!",
        reply_markup=kb_city,
    )


@func_logger("Вводится город...", level="info")
async def add_city(message: types.Message, state: FSMContext) -> None:
    """Get the name of the user's city."""

    if message.text in await get_cities():
        await state.update_data(city=message.text)
        await state.set_state(FSMClientReview.name)
        await message.reply("Введите название заведения (можно не полностью)")
    else:
        await send_message(
            bot,
            message,
            f"Город <b>{message.text}</b> пока не поддерживается",
        )


async def add_place_name(message: types.Message, state: FSMContext) -> None:
    """
    Get the name of the place from the user, search for it in the database,
    and handle the response based on the number of matching results.
    """
    await state.update_data(name=message.text)
    data = await state.get_data()
    places = await search_place_name_in_database(data["name"], data["city"])
    num_places = len(places)
    if num_places == 0:
        await send_message(
            message.bot,
            message,
            NOT_FOUND_PLACE_MESSAGE.format(data["name"]),
        )
    elif num_places == 1:
        place_name = places[0]
        if data["mode"] == "write":
            await send_message(
                message.bot,
                message,
                INPUT_YOUR_MESSAGE.format(place_name),
                reply_markup=ReplyKeyboardRemove(),
            )
            await state.update_data(places=place_name)
            await state.set_state(FSMClientReview.review)
        else:
            await send_message(
                message.bot,
                message,
                await read_review_from_database(place_name, message),
                reply_markup=kb_client,
            )
            await state.clear()
    else:
        buttons = [
            place.name for place in places[:MAX_QUANTITY_OF_PLACES_ON_KB]
        ]
        await send_message(
            message.bot,
            message,
            TOO_GLOBAL_REQUEST.format(data["name"]),
            reply_markup=get_keyboard(buttons),
        )

@func_logger("Добавляется текст отзыва", level="info")
async def add_place_review(message: types.Message, state: FSMContext):
    """Получаем отзыв и сохраняем его в базу данных."""

    await state.update_data(review=message.text)
    data = await state.get_data()
    await add_review_in_database(data["places"], data["review"], message)
    await send_message(
        bot,
        message,
        "Ваш отзыв успешно сохранен",
        reply_markup=kb_client,
    )
    await state.clear()


@func_logger("Старт просмотра отзывов", level="info")
async def start_read_review(message: types.Message, state: FSMContext):
    """Dialog read reviews start."""

    await state.update_data(mode="read")
    await state.set_state(FSMClientReview.city)
    await send_message(bot, message, "Введите город!", reply_markup=kb_city)


async def register_handlers_review(dp: Dispatcher) -> None:
    """Hadlers register."""

    dp.message.register(
        start_read_review,
        IsCurseMessage(),
        F.text.in_(
            {
                "Узнать отзывы",
                "/reviews",
            }
        ),
    )
    dp.message.register(
        start_add_review,
        IsCurseMessage(),
        F.text.in_(
            {
                "Добавить отзыв",
                "/add_review",
            }
        ),
    )
    dp.message.register(
        add_city,
        IsCurseMessage(),
        FSMClientReview.city,
    )
    dp.message.register(
        add_place_name,
        IsCurseMessage(),
        FSMClientReview.name,
    )
    dp.message.register(
        add_place_review,
        IsCurseMessage(),
        FSMClientReview.review,
    )

    dp.message.register(
        start_read_review,
        IsCurseMessage(),
        F.text.capsfold() == "Узнать отзывы",
    )
