from aiogram import types, Router

from telegrambot.creation import bot
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import send_message


router = Router()


@router.message(IsCurseMessage())
async def filtered_send(message: types.Message):
    await send_message(bot, message, 'Пользуйтесь кнопочками с клавиатуры!')

