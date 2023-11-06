import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
import requests_mock
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiohttp import web

from telegrambot.creation import bot, dp
from telegrambot.handlers.clients.basic import start_router
from telegrambot.handlers.clients.FSM_nearest_place import (
    register_handlers_nearest_place, search_place_done,
)
from telegrambot.handlers.clients.FSM_review import register_handlers_review
from telegrambot.tests.utils.mocked_bot import MockedBot
from telegrambot.tests.utils.update import TEST_CHAT, TEST_USER

@pytest.fixture()
def mock_bot():
    return MockedBot()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def storage():
    tmp_storage = MemoryStorage()
    try:
        yield tmp_storage
    finally:
        await tmp_storage.close()


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
    _message = AsyncMock()
    return _message


@pytest_asyncio.fixture()
def mock_send_message(mocker):
    return mocker.patch(
        "telegrambot.handlers.clients.basic.send_message",
        new_callable=AsyncMock,
    )


@pytest.fixture(scope="function")
def mock_send_message_nearest_place(mocker):
    return mocker.patch(
        "telegrambot.handlers.clients.FSM_nearest_place.send_message",
        new_callable=AsyncMock,
    )


@pytest_asyncio.fixture()
def state(storage):
    return FSMContext(
        storage=storage,
        key=StorageKey(
            bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_CHAT.id
        ),
    )


@pytest.fixture
def state_mock():
    return AsyncMock(spec=FSMContext)

