import os
from unittest.mock import AsyncMock

import pytest
import django
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from telegrambot.tests.utils.update import TEST_USER, TEST_CHAT

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gob.settings")
django.setup()
from aiogram import Dispatcher
from telegrambot.tests.utils.mocked_bot import MockedBot


@pytest.mark.asyncio
async def test_start(bot: MockedBot, storage):
    call = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_CHAT.id)
    )
    await
