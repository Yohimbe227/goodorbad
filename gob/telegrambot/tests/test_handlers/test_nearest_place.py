from unittest import TestCase
from unittest.mock import call

import pytest
from deepdiff import DeepDiff

from telegrambot.creation import bot
from telegrambot.keyboards.client_kb import kb_client_categories

from telegrambot.tests.utils.update import get_message, get_update


class TestNearestPlace:
    @pytest.mark.asyncio
    async def test_start_search_place_response(
            self,
            mock_send_message_nearest_place,
            dispatcher
    ):
        """Тест срабатывания хэндлера `start_search_place` на нужные команды.

        Проверяется путем сравнения параметров, с которыми вызывается
        функция `send_message` с ожидаемыми.

        """
        message = get_message(text="/next_place")
        await dispatcher.feed_update(bot, get_update(message))
        # calls = mock_send_message_nearest_place.mock_calls
        calls = mock_send_message_nearest_place.call_args
        # print(calls,)

        expected_args = call(bot, message, "Уточните свои пожелания", reply_markup=kb_client_categories
                          )
        # assert calls == expected_args
        assert DeepDiff(calls, expected_args) == {}
