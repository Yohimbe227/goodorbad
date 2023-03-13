import sqlite3 as sq

from asgiref.sync import sync_to_async

from administration.models import Place, Review
from aiogram.dispatcher import FSMContext
from telegrambot.creation import bot
from telegrambot.decorators import func_logger
from telegrambot.utils import send_message

from gob.settings import BASE_DIR

base = sq.connect(BASE_DIR / 'db.sqlite3')
cur = base.cursor()


def sql_start():
    if base:
        print('Data base connected OK')


async def sql_add_command(state: FSMContext):
    async with state.proxy() as data:
        # print(data._data)

        await Place.objects.acreate(
            **data._data
            # city=data['city'], name=data['name'], review=data['review'],
        )


@func_logger('записали отзыв в базу данных', level='info')
async def add_review_in_database(state: FSMContext):
    async with state.proxy() as data:
        # print(data._data)
        place = await Place.objects.aget(name=data._data['name'])
        review = await Review.objects.acreate(text=data._data['review'])
    place.review_id = review.pk
    await sync_to_async(place.save)()


@func_logger('считывание из базы всех заведений', level='info')
async def sql_data_base(message):
    async for place in Place.objects.all():
        await send_message(
            bot,
            message,
            f'Город: {place.city}\nИмя заведения:{place.name}\nОписание:'
            f'{place.place_type}\nСсылка: {place.url}',
        )


# async def sql_read():
#     return cur.execute('SELECT * FROM places').fetchall()
#
#
# async def sql_delete_command(data):
#     cur.execute('DELETE FROM places WHERE name == ?', (data,))
#     base.commit()
