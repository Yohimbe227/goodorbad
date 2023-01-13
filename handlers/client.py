from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text

from creation import dp, bot
from keyboards.client_kb import kb_client
from aiogram.types import ReplyKeyboardRemove
from database import sqllite_db


# @dp.message_handler(commands=['start', 'help'])
from utils import send_message


async def command_start(message: types.Message):
    try:
        await send_message(bot, message,
                               'Приветственное сообщение', reply_markup=kb_client)
        await message.delete()
    except Exception as err:
        await message.reply(
            f'{err} Общение с ботом через ЛС.\nhttps://t.me/goodorbad_bot')


async def places_all(message: types.Message):
    await sqllite_db.sql_data_base(message)


# @dp.message_handler(commands=['Оботе', ])
async def about_bot(message: types.Message):
    await bot.send_message(message.from_user.id,
                           'Бот для обмена опыта о посещении различных заведений')


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(command_start, commands=['start', 'help', ])
    disp.register_message_handler(about_bot, commands=['о_боте', ])
    disp.register_message_handler(places_all, commands=['место'])
