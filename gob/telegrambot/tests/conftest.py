from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from aiogram import Dispatcher, Bot

from aiogram.fsm.storage.memory import MemoryStorage

from telegrambot.tests.utils.dispatcher import get_dispatcher
from telegrambot.tests.utils.mocked_bot import MockedBot


@pytest.fixture()
def bot():
    return MockedBot()


@pytest.fixture()
def storage():
    return MemoryStorage()


@pytest.fixture()
def dispatcher(storage):
    return get_dispatcher(storage=storage)


@pytest_asyncio.fixture()
async def message():
    _message = AsyncMock()
    return _message


@pytest.fixture
def mock_send_message(mocker):
    return mocker.patch(
        "telegrambot.handlers.clients.basic.send_message",
        new_callable=AsyncMock,
    )


@pytest.fixture
def mock_about_bot(mocker):
    return mocker.patch(
        "telegrambot.handlers.clients.basic.about_bot",
        new_callable=AsyncMock,
    )
