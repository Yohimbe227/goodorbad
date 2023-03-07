from aiogram import types
from aiogram.dispatcher import Dispatcher
from haversine import haversine, Unit

from administration.models import Place
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


@func_logger('отправка местоположения', level='info')
async def get_location(message: types.Message):
    print(list(message.location.values.values()))
    distance = []
    async for place in Place.objects.all().select_related():
        distance.append((place.name, haversine((place.latitude, place.longitude),
                                       tuple(
                                           message.location.values.values()))
                             )
                        )
    nearest_place = sorted(distance, key=lambda place: place[1])

    # print('haversine', nearest_place)
    try:
        await send_message(
            bot, message, nearest_place[0:2],
            reply_markup=kb_client
        )
    except Exception as err:
        print('Непонятная ошибка')


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
    disp.register_message_handler(get_location,
                                  commands=['отправить_мое_местоположение'])
    disp.register_message_handler(get_location, content_types=['location'])
