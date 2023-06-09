"""
Unused module in this version app.
"""
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import IDFilter, Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup

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


async def cm_start(message: types.Message) -> None:
    """
    Starting a dialog to load a new place.

    Args:
        message: message being sent

    """
    await send_message(
        bot,
        message,
        'Приветствую босс!!!',
        reply_markup=kb_admin,
    )
    await FSMAdmin.city.set()
    await message.reply(
        'Введите Ваш город',
        reply_markup=kb_city,
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
        message: message being sent
        state: current state

    """
    async with state.proxy() as data:
        data['city'] = message.text
    await FSMAdmin.next()
    await message.reply('Введите название заведения')


async def load_name(message: types.Message, state: FSMContext) -> None:
    """
    Process the second answer and write it in the dictionary.

    Args:
        message: message being sent
        state: current state
    """
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    await message.reply('Введите описание')


async def load_description(message: types.Message, state: FSMContext) -> None:
    """
    Process the third answer and write it in the dictionary.

    Args:
        message: message being sent
        state: current state
    """
    async with state.proxy() as data:
        data['review'] = message.text
    await database_functions.sql_add_command(state)
    async with state.proxy() as data:
        await send_message(bot, message, str(data._data)[1:-1])
        await send_message(
            bot,
            message,
            'Добавление нового заведения закончено',
        )
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
        cm_start,
        IDFilter(user_id=ID),
        commands=[
            'загрузить',
        ],
        state=None,
    )
    disp.register_message_handler(cancel_handler, state='*', commands='Отмена')
    disp.register_message_handler(
        cancel_handler,
        Text(equals='отмена', ignore_case=True),
        state='*',
    )
    disp.register_message_handler(
        load_city,
        IsCurseMessage(),
        state=FSMAdmin.city,
    )
    disp.register_message_handler(
        load_name,
        IsCurseMessage(),
        state=FSMAdmin.name,
    )
    disp.register_message_handler(
        load_description,
        IsCurseMessage(),
        state=FSMAdmin.description,
    )
    disp.register_callback_query_handler(
        del_callback_run,
        lambda command: command.data and command.data.startswith('del '),
    )
    disp.register_message_handler(delete_item, commands='Удалить')
