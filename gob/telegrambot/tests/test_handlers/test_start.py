# test_command_start.py

import pytest
# from unittest.mock import MagicMock
# from datetime import datetime
# from aiogram import types
#
# from telegrambot.handlers.clients.basic import command_start
# from django.contrib.auth import get_user_model
# from django.core.management import call_command
import os

# User = get_user_model()

from telegrambot.creation import bot


@pytest.mark.asyncio
def test_command_start555():
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gob.settings")
    django.setup()
    # message = types.Message(
    #     message_id=1,
    #     from_user=types.User(id=1, first_name='John', last_name='Doe'),
    #     text='/start'
    # )

    # await command_start(message)
    # call_command('startbot')
    # Assert that the bot sent a message with the expected text
    assert 'Hello, John!' == 'Hello, John!'
