import os
import pytest
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gob.settings")
django.setup()
from aiogram import Dispatcher
from aiogram.methods import SendMessage

from telegrambot.tests.utils.update import get_update, get_message




@pytest.mark.asyncio
async def test_start(bot: MockedBot, dp: Dispatcher):
    start_command = get_update(get_message('/start'))
    result = await dp.feed_update(bot, start_command)
    # assert isinstance(result, SendMessage)
    # assert result.text == ('Привет! Это JulianPR, который поможет тебе в раскрутке или наоборот поможет '
    #     'заработать денег! Для того, чтобы начать регистрацию, нажми на кнопку внизу!')
    # assert result.reply_markup == 'dljkl;sd'
