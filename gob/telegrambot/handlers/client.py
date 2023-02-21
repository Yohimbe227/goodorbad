from aiogram import types
from aiogram.dispatcher import Dispatcher

from telegrambot.creation import bot
from telegrambot.database import sqllite_db
from telegrambot.decorators import func_logger
from telegrambot.keyboards.client_kb import kb_client
# @dp.message_handler(commands=['start', 'help'])
from telegrambot.utils import send_message


async def command_start(message: types.Message):
    try:
        await send_message(
            bot, message, 'Приветственное сообщение', reply_markup=kb_client
        )
        await message.delete()
    except Exception as err:
        await message.reply(
            f'{err} Общение с ботом через ЛС.\nhttps://t.me/goodorbad_bot'
        )


@func_logger('вывод всех заведений', level='info')
async def places_all(message: types.Message):
    await sqllite_db.sql_data_base(message)


# @dp.message_handler(commands=['Оботе', ])
@func_logger('вывод сообщения о боте', level='info')
async def about_bot(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        'Бот для обмена опыта о посещении различных заведений',
    )


# @dp.message_handler(content_types=['photo', ], state=FSMAdmin.photo)
# async def load_photo(message: types.Message, state: FSMContext) -> None:
#     """
#     Process the first answer and write it in the dictionary.
#
#     Args:
#         message: message being sent
#         state: current state
#     """
#     async with state.proxy() as data:
#         data['photo'] = message.photo[0].file_id
#     await FSMAdmin.next()
#     await message.reply('Введите Ваш город')


def register_handlers_client(disp: Dispatcher):
    disp.register_message_handler(
        command_start,
        commands=[
            'start',
            'help',
        ],
    )
    disp.register_message_handler(
        about_bot,
        commands=[
            'о_боте',
        ],
    )
    disp.register_message_handler(places_all, commands=['место'])
