"""
Module for admin.
"""
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from django.core.management import call_command

from aiogram import Dispatcher, types, F, filters, Router

from aiogram.types import InlineKeyboardMarkup
from asgiref.sync import sync_to_async

from telegrambot.costants import ID
from telegrambot.creation import bot
from telegrambot.database import database_functions
from telegrambot.keyboards.client_kb import kb_client
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import send_message


class FSMAdmin(StatesGroup):
    """Class of states."""

    city = State()


router = Router()


@router.message(F.from_user.id == ID, Command(commands=['загрузить', ]), )
async def city_add(message: types.Message, state: FSMContext) -> None:
    """
    Starting a dialog to load a new city.

    Args:
        state: current state
        message: message being sent

    """
    await send_message(
        bot,
        message,
        'Приветствую босс!!!',
    )
    await state.set_state(FSMAdmin.city)
    await message.reply(
        'Введите город для добавления в базу',
    )


@router.message(FSMAdmin.city, F.text, )
async def save_city_to_base(message: types.Message, state: FSMContext) -> None:
    """Process the first answer and write it in the dictionary.

    Args:
        message: message being sent.
        state: current state.

    """
    await sync_to_async(call_command)('update', city=message.text)
    await send_message(bot, message, f'Город {message.text} добавлен!')
    await state.clear()


@router.message(F.text.lower().in_({'отмена', 'вернуться'}))
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    """Exit from the state.

    Args:
        message: Message being sent.
        state: Current state.

    """
    print('cancel handelr activated')
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.reply('OK', reply_markup=kb_client)


# def register_handlers_admin(disp: Dispatcher) -> None:
#     """
#     Handler registration.
#
#     Args:
#         disp: Dispatcher object

    # """
    # disp.register_message_handler(
    #     city_add,
    #     IDFilter(user_id=ID),
    #     commands=[
    #         'загрузить',
    #     ],
    #     state=None,
    # )
    # disp.register_message_handler(
    #     cancel_handler,
    #     Text(equals=['отмена', 'вернуться'], ignore_case=True),
    #     state='*',
    # )
    # disp.register_message_handler(
    #     save_city_to_base,
    #     IsCurseMessage(),
    #     state=FSMAdmin.city,
    # )
