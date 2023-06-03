from aiogram import Dispatcher, types

from telegrambot.creation import bot
from telegrambot.moderator import IsCurseMessage


async def filtered_send(message: types.Message):

    if user_location := message.location:
        print(user_location)
    else:
        await bot.send_message(message.from_user.id, message.text)


def register_handlers_other(disp: Dispatcher):
    disp.register_message_handler(filtered_send, IsCurseMessage())
