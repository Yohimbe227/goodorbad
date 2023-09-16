import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update, Message

from telegrambot.creation import dp
from telegrambot.handlers.clients.FSM_nearest_place import \
    register_handlers_nearest_place
from telegrambot.handlers.clients.FSM_review import register_handlers_review
from telegrambot.handlers.clients.basic import start_router
from telegrambot.tests.utils.mocked_bot import MockedBot
from telegrambot.tests.utils.update import get_update


@pytest.fixture()
def mock_bot():
    return MockedBot()


@pytest.fixture(scope="session")
def storage():
    return MemoryStorage()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def dispatcher():
    dp.__config__ = {'validate_assignment': False}
    dp.include_router(start_router)
    await register_handlers_nearest_place(dp)
    await register_handlers_review(dp)
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()


@pytest_asyncio.fixture()
def message():
    _message = MagicMock()
    return _message


@pytest.fixture()
def update(message):
    _update = get_update(message)
    _update.update_id = 128
    _update.message = message
    _update.__config__ = {'validate_assignment': False}
    return _update


@pytest_asyncio.fixture()
def mock_send_message(mocker):
    return mocker.patch(
        "telegrambot.handlers.clients.basic.send_message",
        new_callable=AsyncMock,
    )


@pytest.fixture
def mock_about_bot_handler(mocker):
    return mocker.patch(
        "telegrambot.handlers.clients.basic.about_bot",
        new_callable=AsyncMock,
    )


@pytest.fixture(scope="function")
def mock_send_message_nearest_place(mocker):
    return mocker.patch(
        "telegrambot.handlers.clients.FSM_nearest_place.send_message",
        new_callable=AsyncMock,
    )
