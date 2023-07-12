"""
Unused module in this version app.
"""
from django.core.management import call_command

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import IDFilter, Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup
from asgiref.sync import sync_to_async

from telegrambot.costants import ID
from telegrambot.creation import bot
from telegrambot.database import database_functions
from telegrambot.keyboards.admin_kb import kb_admin
from telegrambot.keyboards.city_kb import kb_city
from telegrambot.keyboards.client_kb import kb_client
from telegrambot.moderator import IsCurseMessage
from telegrambot.utils import send_message


class FSMAdmin(StatesGroup):
    """Class of states."""

    city = State()
    name = State()
    description = State()


async def city_add(message: types.Message) -> None:
    """
    Starting a dialog to load a new city.

    Args:
        message: message being sent

    """
    await send_message(
        bot,
        message,
        'Приветствую босс!!!',
    )
    await FSMAdmin.city.set()
    await message.reply(
        'Введите город для добавления в базу',
    )


async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    """Exit from the state.

    Args:
        message: message being sent
        state: current state

    """
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('OK', reply_markup=kb_client)


async def load_city(message: types.Message, state: FSMContext) -> None:
    """Process the first answer and write it in the dictionary.

    Args:
        message: message being sent.
        state: current state.

    """
    await sync_to_async(call_command)('update', city=message.text)
    await send_message(bot, message, f'Город {message.text} добавлен!')
    await state.finish()


async def del_callback_run(callback_query: types.CallbackQuery) -> None:
    """
    Deleting a place.

    Args:
        callback_query: callback query
    """
    await database_functions.sql_delete_command(
        callback_query.data.replace(
            'del ',
            '',
        ),
    )
    await callback_query.answer(
        text=f'{callback_query.data.replace("del ", "")} удалена.',
        show_alert=True,
    )


async def delete_item(message: types.Message) -> None:
    """
    Issuing a database to delete a part of it.

    Args:
        message: message being sent
    """
    if message.from_user.id == ID:
        read = await database_functions.sql_read()
        for value in read:
            await send_message(
                bot,
                message,
                f'Город: {value[0]}\nИмя заведения:{value[1]}'
                f'\nОписание:{value[2]}',
            )
            await send_message(
                bot,
                message,
                '^^^',
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardMarkup(
                        text=f'Удалить {value[1]}',
                        callback_data=f'del {value[1]}',
                    ),
                ),
            )


def register_handlers_admin(disp: Dispatcher) -> None:
    """
    Handler registration.

    Args:
        disp: Dispatcher object

    """
    disp.register_message_handler(
        city_add,
        IDFilter(user_id=ID),
        commands=[
            'загрузить',
        ],
        state=None,
    )
    disp.register_message_handler(
        cancel_handler,
        Text(equals=['отмена', 'вернуться'], ignore_case=True),
        state='*',
    )
    disp.register_message_handler(
        load_city,
        IsCurseMessage(),
        state=FSMAdmin.city,
    )

    disp.register_callback_query_handler(
        del_callback_run,
        lambda command: command.data and command.data.startswith('del '),
    )
    disp.register_message_handler(delete_item, commands='Удалить')
