import asyncio
import os
from copy import copy

import pytest
import django
from aiogram import Dispatcher

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gob.settings")
django.setup()

from telegrambot.tests.utils.dispatcher import get_dispatcher
from telegrambot.tests.utils.mocked_bot import MockedBot
from django.contrib.auth import get_user_model
from telegrambot.costants import START_MESSAGE, ABOUT_MESSAGE
from telegrambot.creation import bot
from telegrambot.keyboards.client_kb import kb_client
from telegrambot.handlers.clients.basic import command_start, start_router
from telegrambot.tests.utils.update import (
    TEST_MESSAGE,
    FIRST_TIME_USER,
    get_message, get_update,
)
from telegrambot.creation import bot as realbot

User = get_user_model()


class TestStartCommand:
    _params_user = {
        "username": TEST_MESSAGE.from_user.id,
        "last_name": TEST_MESSAGE.from_user.last_name,
        "first_name": TEST_MESSAGE.from_user.first_name,
    }
    params_user = {key: value for key, value in _params_user.items() if value}

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_command_start(self, django_db_blocker, mock_send_message):
        with django_db_blocker.unblock():
            await User.objects.acreate(**self.params_user)
            await command_start(TEST_MESSAGE)
            mock_send_message.assert_called_with(
                bot,
                TEST_MESSAGE,
                f"И снова здравствуйте {TEST_MESSAGE.from_user.first_name}!",
                reply_markup=kb_client,
            )

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_command_start_first_time(
            self, django_db_blocker, mock_send_message
    ):
        with django_db_blocker.unblock():
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

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    async def test_command_start_error(
            self, django_db_blocker, mock_send_message
    ):
        with django_db_blocker.unblock():
            await command_start(TEST_MESSAGE)
            loop = asyncio.get_event_loop()
            user_exists = await loop.run_in_executor(
                None,
                User.objects.filter(username=TEST_MESSAGE.from_user.id).exists,
            )
            assert user_exists

    # @pytest.mark.asyncio
    # @pytest.mark.parametrize("command", [("/start",), ("старт",), ("старт",)])
    # async def test_handler_start(self, bot, message, dispatcher, command):
    #     dispatcher.register_message_handler(
    #         command_start, Command(command)
    #     )
    #     message.text = "command"
    #     await bot.send_message(message)
    #     assert command_start.called


class TestAbout:

    dispatcher = get_dispatcher()

    @pytest.mark.asyncio
    async def test_handler_about(self, bot: MockedBot, mock_send_message):

        message = get_message(text="/about")
        await self.dispatcher.feed_update(bot, get_update(message))
        await mock_send_message.assert_called_with(
            realbot,
            message,
            ABOUT_MESSAGE,
            reply_markup=kb_client,
        )
