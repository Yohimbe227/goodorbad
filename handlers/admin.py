from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup

from creation import dp, bot
from database import sqllite_db
from keyboards import admin_kb

ID = None


class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()


# Получаем ID текущего модератора
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    await bot.send_message(message.from_user.id, 'Слушаю, босс.',
                           reply_markup=admin_kb.button_case_admin)
    await message.delete()


# Начало диалога загрузки нового заведения
# @dp.message_handler(commands='Загрузить', state=None)
async def cm_start(message: types.Message):
    if message.from_user.id == ID:
        await FSMAdmin.photo.set()
        await message.reply('Загрузи фото')


# Выход из состояния
# @dp.message_handler(state='*', commands='Отмена')
# @dp.register_message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK')


# Ловим первый ответ и пишем в словарь
# @dp.message_handler(content_types=['photo', ], state=FSMAdmin.photo)
async def load_photo(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['photo'] = message.photo[0].file_id
        await FSMAdmin.next()
        await message.reply('Введите название')


# Ловим второй ответ
# @dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await message.reply('Введите описание')


# Ловим третий ответ
# @dp.message_handler(state=FSMAdmin.description)
async def load_description(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['description'] = message.text
        await sqllite_db.sql_add_command(state)
        async with state.proxy() as data:
            await message.reply(str(data))
            await message.reply('Добавление нового заведения закончено')
        await state.finish()


async def del_callback_run(callback_query: types.CallbackQuery):
    await sqllite_db.sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} удалена.', show_alert=True)


async def delete_item(message: types.Message):
    if message.from_user.id == ID:
        read = await sqllite_db.sql_read()
        for ret in read:
            await bot.send_photo(message.from_user.id, ret[0],
                                 f'{ret[1]}\nГород: {ret[2]}\nИмя заведения {ret[-1]}')
            await bot.send_message(message.from_user.id, text='^^^',
                                   reply_markup=InlineKeyboardMarkup().add(
                                       InlineKeyboardMarkup(
                                           f'Удалить {ret[1]}',
                                           callback_data=f'del {ret[1]}')))


def register_handlers_admin(disp: Dispatcher):
    disp.register_message_handler(cm_start, commands=['Загрузить', ],
                                  state=None)
    disp.register_message_handler(cancel_handler, state='*', commands='Отмена')
    disp.register_message_handler(cancel_handler,
                                  Text(equals='отмена', ignore_case=True),
                                  state='*')
    disp.register_message_handler(load_photo, content_types=['photo', ],
                                  state=FSMAdmin.photo)
    disp.register_message_handler(load_name, state=FSMAdmin.name)
    disp.register_message_handler(load_description, state=FSMAdmin.description)
    disp.register_message_handler(make_changes_command, commands=['moderator'],
                                  is_chat_admin=True)
