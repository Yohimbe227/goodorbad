import sqlite3 as sq

from administration.models import Place, Review, User
from aiogram import types
from aiogram.dispatcher import FSMContext
from asgiref.sync import sync_to_async
from django.db.models import QuerySet
from telegrambot.creation import bot
from telegrambot.decorators import func_logger
from telegrambot.utils import send_message

from gob.settings import BASE_DIR

base = sq.connect(BASE_DIR / 'db.sqlite3')


def sql_start():
    if base:
        print('Data base connected OK')


@func_logger('ищем заведение по названию в БД', level='info')
async def search_place_name_in_database(place_name):
    @sync_to_async
    def get_place_value(name: str) -> list[Place]:
        return list(
            Place.objects.filter(name__icontains=name[1:])
        )  # Из-за sqlite не работает поиск без ^^^^^^^^^ регистра, поэтому костыль

    return await get_place_value(place_name)


@func_logger('создаем объект отзыва', level='info')
async def add_review_in_database(
    place: Place, review_text: str, message: types.Message
) -> None:
    user = await User.objects.aget(username=message.from_user.id)
    await Review.objects.acreate(
        text=review_text, place_id=place.pk, author_id=user.pk
    )


async def read_review_from_database(place: Place, message: types.Message):
    place = await search_place_name_in_database(place.name)

    @sync_to_async
    def get_review_list(place: list[Place]):
        reviews = Review.objects.filter(place=place[0].pk).select_related(
            'place', 'author'
        )
        user = User.objects.get(username=message.from_user.id)
        return reviews.exclude(author_id=user.pk).order_by(
            'date'
        ), reviews.filter(author_id=user.pk).order_by('date')

    return await get_review_list(place)


@func_logger('считывание из базы всех заведений', level='info')
async def sql_data_base(message: types.Message):
    async for place in Place.objects.all():
        await send_message(
            bot,
            message,
            f'Город: {place.city}\nИмя заведения:{place.name}\nОписание:'
            f'{place.place_type}\nСсылка: {place.url}',
        )
