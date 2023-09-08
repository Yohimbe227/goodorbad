import os
from copy import copy

import pytest
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gob.settings")
django.setup()

from telegrambot.costants import START_MESSAGE
from telegrambot.creation import bot
from telegrambot.keyboards.client_kb import kb_client

from telegrambot.handlers.clients.basic import command_start
from telegrambot.tests.utils.update import TEST_MESSAGE, FIRST_TIME_USER, \
    get_message


@pytest.mark.asyncio
async def test_command_start(mock_send_message):
    await command_start(TEST_MESSAGE)
    mock_send_message.assert_called_with(
        bot,
        TEST_MESSAGE,
        f"И снова здравствуйте {TEST_MESSAGE.from_user.first_name}!",
        reply_markup=kb_client,
    )


@pytest.mark.asyncio
async def test_command_start_first_time(mock_send_message):
    first_time_message = get_message(
        START_MESSAGE.format(
            username=FIRST_TIME_USER.first_name,
        ),
        from_user=FIRST_TIME_USER,
    )
    await command_start(first_time_message)
    mock_send_message.assert_called_with(
        bot,
        first_time_message,
        START_MESSAGE.format(username=FIRST_TIME_USER.first_name),
        reply_markup=kb_client,
    )
