from aiogram import Dispatcher, types

from telegrambot.creation import bot
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import send_message


async def filtered_send(message: types.Message):
    await send_message(bot, message, 'Пользуйтесь кнопочками с клавиатуры!')


def register_handlers_other(disp: Dispatcher):
    disp.register_message_handler(filtered_send, IsCurseMessage())
