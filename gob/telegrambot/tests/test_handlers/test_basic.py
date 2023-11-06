import asyncio
import os
from unittest import mock

import django

import pytest
from pytest_mock import mocker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gob.settings")
django.setup()

from django.contrib.auth import get_user_model

from telegrambot.costants import ABOUT_MESSAGE, HR_ATTENTION, ID, START_MESSAGE
from telegrambot.creation import bot
from telegrambot.handlers.clients.basic import command_start
from telegrambot.keyboards.client_kb import kb_client
from telegrambot.tests.utils.update import (
    FIRST_TIME_USER,
    TEST_MESSAGE,
    get_message,
    get_update,
)

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

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "command",
        [
            "/start",
            "старт",
            "start",
        ],
    )
    async def test_handler_start(self, mock_send_message, dispatcher, command):

        message = get_message(text=command)
        await dispatcher.feed_update(bot, get_update(message))
        mock_send_message.assert_called()


class TestAbout:
    @pytest.mark.parametrize("command", ["about", "/about", "о боте"])
    @pytest.mark.asyncio
    async def test_handler_about(self, mock_send_message, dispatcher, command):
        """Тест срабатывания хэндлера `about_bot` на нужные комманды.

        Проверяется путем сравнения параметров, с которыми вызывается
        функция `send_message` с ожидаемыми.

        """
        message = get_message(text=command)
        await dispatcher.feed_update(bot, get_update(message))
        mock_send_message.assert_called()


class TestHR:
    @pytest.mark.asyncio
    async def test_handler_about(
        self,
        mock_send_message,
        dispatcher,
        mock_bot,
    ):
        """Тест срабатывания хэндлера `hr_attention` на нужную комманду.

        Проверяется путем сравнения параметров, с которыми вызывается
        функция `send_message` с ожидаемыми.

        """
        message = get_message(text="Я HR и мне нравится!")
        with mock.patch.object(
            bot, "send_message"
        ) as mock_send_message_method:
            await dispatcher.feed_update(mock_bot, get_update(message))
            mock_send_message_method.assert_called_with(ID, HR_ATTENTION)
        assert mock_send_message.call_count == 2
