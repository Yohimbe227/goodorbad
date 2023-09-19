import pytest

from telegrambot.costants import (
    LOCATION_REQUEST,
    NO_PLACE_PRESENTED,
    PLACE_TYPES,
)
from telegrambot.creation import bot
from telegrambot.handlers.clients.FSM_nearest_place import (
    FSMClientSearchPlace,
    search_place_request_location,
    start_search_place,
)
from telegrambot.keyboards.client_kb import (
    get_keyboard,
    kb_client_categories,
    kb_client_location,
)
from telegrambot.tests.test_handlers.utils import (
    compare_lists,
    get_attribute_list,
)
from telegrambot.tests.utils.update import (
    TEST_MESSAGE,
    get_message,
    get_update,
)


class StartSearchPlace:
    """Тесты хэндлера `start_search_place`"""

    @pytest.mark.asyncio
    async def test_start_search_place_response(
            self, mock_send_message_nearest_place, dispatcher
    ):
        """Тест срабатывания хэндлера `start_search_place` на нужные команды.

        Проверяется путем сравнения параметров, с которыми вызывается
        функция `send_message` с ожидаемыми.

        """
        message = get_message(text="/next_place")
        await dispatcher.feed_update(bot, get_update(message))
        expected_args = [
            bot,
            message,
            "Уточните свои пожелания",
            kb_client_categories,
        ]
        assert compare_lists(
            get_attribute_list(mock_send_message_nearest_place), expected_args
        )

    @pytest.mark.asyncio
    async def test_state_first(
            self, mock_send_message_nearest_place, state,
    ):
        """Проверяем состояние `state` после срабатывания `start_search_place`."""

        await start_search_place(TEST_MESSAGE, state=state)
        assert await state.get_state() == FSMClientSearchPlace.first


class TestSearchPlaceRequestLocation:

    @pytest.mark.parametrize("message_text", list(PLACE_TYPES.keys()))
    @pytest.mark.asyncio
    async def test_state_first(
            self, mock_send_message_nearest_place, message_text, state
    ):
        """Проверяем состояние `state`.

        После срабатывания `search_place_request_location`.

        """
        await search_place_request_location(
            get_message(message_text), state=state
        )
        assert await state.get_state() == FSMClientSearchPlace.second

    @pytest.mark.asyncio
    async def test_wrong_place_category(self, mock_send_message_nearest_place,
                                        state):
        """Проверяем состояние `state`.

        После срабатывания `search_place_request_location`.

        """
        message = get_message("случайное слово")
        await search_place_request_location(message, state=state)
        expected_args = [
            bot,
            message,
            NO_PLACE_PRESENTED,
            get_keyboard(PLACE_TYPES.keys()),
        ]
        assert compare_lists(
            get_attribute_list(mock_send_message_nearest_place), expected_args
        )


class TestSearchPlaceDone:
    ...
