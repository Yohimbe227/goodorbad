import sqlite3 as sq
from asyncio import get_event_loop

from bot_admin.models import Place
from gob.settings import BASE_DIR
from telegrambot.creation import bot
from telegrambot.decorators import func_logger
from asgiref.sync import sync_to_async

base = sq.connect(BASE_DIR / 'db.sqlite3')
cur = base.cursor()


def sql_start():

    if base:
        print('Data base connected OK')
    # base.execute(
    #     'CREATE TABLE IF NOT EXISTS places(img TEXT, name TEXT PRIMARY KEY, description TEXT)'
    # )
    # base.commit()


# async def sql_add_command(state):
#     async with state.proxy() as data:
#         cur.execute(
#             'INSERT INTO places VALUES (?, ?, ?)', tuple(data.values())
#         )
#         base.commit()

# @sync_to_async
# def get_users():
#     return list(
#         Place.objects.all()
#     )
@sync_to_async
def get_all_places():
    return list(Place.objects.all())


# @func_logger('считывание из базы всех заведений', level='info')
async def sql_data_base(message):

    # get_place = sync_to_async(Place.objects.all)()
    # print(get_place, type(get_place))
    results = await get_all_places()
    for value in results:
        print(value.name)

    loop = get_event_loop()
    loop.run_until_complete(sql_data_base(message))
        # bot.send_message(
        #     message.from_user.id,
        #     f'Город: {value.city}\nИмя заведения:{value.name}\nОписание:{value.place_type}',
        # )


async def sql_read():
    return cur.execute('SELECT * FROM places').fetchall()


async def sql_delete_command(data):
    cur.execute('DELETE FROM places WHERE name == ?', (data,))
    base.commit()
