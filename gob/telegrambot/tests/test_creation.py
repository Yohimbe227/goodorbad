import os

import pytest
from aiogram import Bot
from aiogram.utils.token import TokenValidationError

from telegrambot.costants import TELEGRAM_TOKEN


class TestCreation:
    tokens = (
        "DB_ENGINE",
        "DB_NAME",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "DB_HOST",
        "DB_PORT",
        "TELEGRAM_TOKEN",
        "TELEGRAM_TO",
        "YA_TOKEN",
        "YA_GEO_TOKEN",
        "TELEGRAM_TOKEN_FOR_MESSAGE",
        "SECRET_KEY",
    )

    @pytest.mark.parametrize("token", tokens)
    def test_tokens_available(self, token):
        """Проверяем доступность токенов в переменных окружения"""

        assert os.getenv(token) is not None
        match token:
            case "TELEGRAM_TOKEN":
                assert len(os.getenv(token)) > 30
            case "DB_ENGINE":
                assert os.getenv(token).count(".") > 2
            case "DB_PORT":
                assert os.getenv(token).isalnum()
            case "SECRET_KEY":
                if token is not None:
                    assert len(os.getenv(token))
