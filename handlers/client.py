from aiogram import types
from aiogram.dispatcher import Dispatcher

from bot_creation import dp, bot


# @dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    try:
        await bot.send_message(message.from_user.id,
                               'Приветственное сообщение', )
        await message.delete()
    except Exception:
        await message.reply(
            'Общение с ботом через ЛС.\nhttps://t.me/goodorbad')


# @dp.message_handler(commands=['Оботе', ])
async def about_bot(message: types.Message):
    await bot.send_message(message.from_user.id,
                           'Бот для обмена опыта о посещении различных заведений')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help', ])
    dp.register_message_handler(about_bot, commands=['О_боте', ])
