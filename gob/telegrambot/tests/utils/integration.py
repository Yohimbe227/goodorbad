from collections import deque
from typing import TYPE_CHECKING, AsyncGenerator, Deque, Optional, Type

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import TelegramMethod
from aiogram.methods.base import Request, Response, TelegramType
from aiogram.types import ResponseParameters, User
from aiogram_tests.mocked_bot import MockedSession
