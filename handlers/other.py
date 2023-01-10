from aiogram import types, Dispatcher

from bot_creation import bot, dp
from moderator import filter_word


async def filtered_send(message: types.Message):
    if filter_word(message.text):
        await message.reply('А ну не матюкаться!')
        await message.delete()
    else:
        await bot.send_message(message.from_user.id, message.text)


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(filtered_send)

