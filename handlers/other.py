from aiogram import Dispatcher, types

from creation import bot, dp
# from moderator import filter_word
from moderator import IsCurseMessage


async def filtered_send(message: types.Message):
    # if filter_word(message.text):
    #     await message.reply('А ну не матюкаться!')
    #     await message.delete()
    # else:
    await bot.send_message(message.from_user.id, message.text)


def register_handlers_other(disp: Dispatcher):
    disp.register_message_handler(filtered_send, IsCurseMessage())
