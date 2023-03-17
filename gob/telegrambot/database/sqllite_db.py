import sqlite3 as sq

from administration.models import Place, Review
from aiogram import types
from aiogram.dispatcher import FSMContext
from asgiref.sync import sync_to_async
from telegrambot.creation import bot
from telegrambot.decorators import func_logger
from telegrambot.utils import send_message

from gob.settings import BASE_DIR

base = sq.connect(BASE_DIR / 'db.sqlite3')
cur = base.cursor()


def sql_start():
    if base:
        print('Data base connected OK')


# async def sql_add_command(state: FSMContext):
#     async with state.proxy() as data:
#         await Place.objects.acreate(
#             **data._data
#             # city=data['city'], name=data['name'], review=data['review'],
#         )


@func_logger('ищем заведение по названию в БД', level='info')
async def search_place_name_in_database(place_name):
    @sync_to_async
    def get_place_value(name: str) -> list[Place]:
        return list(
            Place.objects.filter(name__icontains=name[1:])
        )  # Из-за sqlite не работает поиск без ^^^^^^^^^ регистра, поэтому костыль

    return await get_place_value(place_name)


@func_logger('создаем объект отзыва', level='info')
async def add_review_in_database(place: Place, review_text: str) -> None:
    await Review.objects.acreate(text=review_text, place_id=place.pk)


async def read_review_from_database(place: Place):
    place = await search_place_name_in_database(place.name)

    @sync_to_async
    def get_review_list(place: list[Place]) -> list[Place]:

        return Review.objects.filter(place=place[0].pk).select_related('place')
    return await get_review_list(place)


@func_logger('считывание из базы всех заведений', level='info')
async def sql_data_base(message):
    async for place in Place.objects.all():
        await send_message(
            bot,
            message,
            f'Город: {place.city}\nИмя заведения:{place.name}\nОписание:'
            f'{place.place_type}\nСсылка: {place.url}',
        )
