from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from aiogram import Dispatcher

from aiogram.fsm.storage.memory import MemoryStorage

from telegrambot.tests.utils.mocked_bot import MockedBot


@pytest_asyncio.fixture(scope="session")
async def storage():
    tmp_storage = MemoryStorage()
    try:
        yield tmp_storage
    finally:
        await tmp_storage.close()


@pytest_asyncio.fixture()
def bot():
    return MockedBot()


@pytest_asyncio.fixture()
async def dispatcher():
    dp = Dispatcher()
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()


@pytest_asyncio.fixture()
async def message():
    _message = AsyncMock()
    return _message


@pytest.fixture
def mock_send_message(mocker):
    return mocker.patch(
        "telegrambot.handlers.clients.basic.send_message", new_callable=AsyncMock
    )
