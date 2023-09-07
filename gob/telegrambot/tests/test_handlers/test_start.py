import os
from datetime import datetime

import pytest
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gob.settings")
django.setup()
from telegrambot.creation import bot
from telegrambot.keyboards.client_kb import kb_client
from telegrambot.tests.utils.mocked_bot import MockedBot


from telegrambot.handlers.clients.basic import command_start
from telegrambot.tests.utils.update import TEST_CHAT, TEST_USER, TEST_MESSAGE


@pytest.mark.asyncio
async def test_command_start(mock_send_message):

    await command_start(TEST_MESSAGE)
    mock_send_message.assert_called_with(
        bot,
        TEST_MESSAGE,
        f'И снова здравствуйте {TEST_MESSAGE.from_user.first_name}!',
        reply_markup=kb_client,
    )
