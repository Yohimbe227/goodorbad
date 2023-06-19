"""
The module in which most database calls are made.
"""

from django.db.models import Q

from aiogram import types
from asgiref.sync import sync_to_async
from haversine import haversine

from administration.models import City, Place, Review, User
from telegrambot.costants import M_IN_KM, MAX_RANGE_SEARCH, PLACE_TYPES
from telegrambot.creation import bot
from telegrambot.decorators import func_logger
from telegrambot.exceptions import ReviewBecomeError
from telegrambot.utils import logger, send_message


@func_logger('Ищем заведение по названию в БД', level='info')
async def search_place_name_in_database(
    place_name: str,
    city: str,
) -> list[Place]:
    """Search `Place` object by name and city in database.

    Args:
        place_name: name of place.
        city: place city.

    Returns:
        Place objects filtered by name.

    """

    @sync_to_async
    def get_place_value(name: str) -> list[Place]:
        """
        This is an auxiliary function for performing synchronous actions
        with the database in an asynchronous function.
        """
        return list(
            Place.objects.filter(Q(name__icontains=name) & Q(city__name=city)),
        )

    return await get_place_value(place_name)


@func_logger('создаем объект отзыва', level='info')
async def add_review_in_database(
    place: Place,
    review_text: str,
    message: types.Message,
) -> None:
    """Add `review` object in database.

    Args:
        place: `Place` object.
        review_text: Review text.
        message: `message` object from user.

    """
    user = await User.objects.aget(username=message.from_user.id)
    await Review.objects.acreate(
        text=review_text,
        place_id=place.pk,
        author_id=user.pk,
    )


@sync_to_async
def city_name(place_obj):
    return place_obj.city.name


async def read_review_from_database(place: Place, message: types.Message):
    """
    Считываем отзывы из базды данных и подготавливаем строку с соответствующим
    сообщением пользователю.

    Args:
        place: объект заведения `Place`.
        message: `message` object from user.

    Returns:
        Строка с подготовленным сообщением для пользователя.

    """
    place = await search_place_name_in_database(place.name, await city_name(place))

    @sync_to_async
    def get_review_list(place: list[Place]) -> str:
        """
        This is an auxiliary function for performing synchronous actions
        with the database in an asynchronous function.
        """
        try:
            reviews = Review.objects.filter(place=place[0].pk).select_related(
                'place',
                'author',
            )
        except Exception:
            logger.critical('Проблемы со считыванием отзывов из базы данных')
            raise ReviewBecomeError

        user = User.objects.get(username=message.from_user.id)

        reviews_other_text = [
            review.text
            for review in reviews.exclude(author_id=user.pk).order_by('date')
        ]
        reviews_user_text = [
            review.text
            for review in reviews.filter(author_id=user.pk).order_by('date')
        ]
        if reviews_user_text and reviews_other_text:
            return '\n'.join(
                ['<b>Мои отзывы:</b>']
                + reviews_user_text
                + ['<b>Все отзывы:</b>']
                + reviews_other_text,
            )
        elif not reviews_user_text and reviews_other_text:
            return (
                '\n'.join(['<b>Все отзывы:</b>'] + reviews_other_text)
                if reviews_other_text or reviews_user_text
                else 'Отзывов пока нет, но Вы можете добавить'
            )
        elif reviews_user_text and not reviews_other_text:
            return '\n'.join(['<b>Мои отзывы:</b>'] + reviews_user_text)
        else:
            return 'Отзывов пока нет, но Вы их можете добавить'

    return await get_review_list(place)


@func_logger('считывание из базы всех заведений', level='info')
async def read_all_data_from_base(message: types.Message) -> None:
    """Reading all `Place` data from database.

    Args:
        message: `message` object from user.

    """
    async for place in Place.objects.all():
        await send_message(
            bot,
            message,
            f'Город: {place.city}\nИмя заведения:{place.name}\nОписание:'
            f'{place.category}\nСсылка: {place.url}',
        )


@func_logger('Поднимаем базу для подсчета расстояний', level='info')
async def read_places_coordinates(
    location,
    _category: str,
) -> list[tuple[Place, float]]:
    """
    Calculate the distances between the user's location and all
    establishments of the desired type.


    Args:
        location: coordinates of place.
        _category: тип заведения (кафе, бар, ресторан и т.п.).

    Returns:
        Список кортежей с названием города, названием заведения и расстоянием
        до местоположения пользователя.

    """

    distance_to_place = []
    async for place in Place.objects.filter(
        category__name__in=PLACE_TYPES[_category.lower()],
    ).prefetch_related('category'):
        _distance = haversine(
            (place.latitude, place.longitude),
            list(map(float, location)),
        )
        if _distance < MAX_RANGE_SEARCH / M_IN_KM:
            distance_to_place.append(
                (
                    place,
                    _distance,
                ),
            )
    return distance_to_place


async def get_cities():
    @sync_to_async()
    def _get_cities():
        cities = City.objects.all().select_related().order_by('name')
        return [city.name for city in cities]

    return await _get_cities()
