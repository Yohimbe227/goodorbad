from aiogram import types
from aiogram.bot import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from telegrambot.decorators import func_logger
from telegrambot.keyboards.city_kb import kb_city
from telegrambot.utils import send_message


class FSMClientChooseType(StatesGroup):

    city = State()
    name = State()
    review = State()


@func_logger('старт выбора типа заведения', level='info')
async def start_add_review(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['mode'] = 'write'
    await FSMClientChooseType.city.set()
    await send_message(
        bot, message, 'Введите Ваш город!', reply_markup=kb_city
    )
