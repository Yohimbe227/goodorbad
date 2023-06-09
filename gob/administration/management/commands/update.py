"""
Fills out or updates the database of institutions.
It uses the yandex API.
"""
import logging
import os
import time
from http import HTTPStatus
from itertools import chain
from logging.handlers import RotatingFileHandler

from django.core.management import BaseCommand
from django.db import IntegrityError
from django.utils.dateparse import parse_time

import requests

from administration.models import Category, CategoryPlace, City, Place
from telegrambot.decorators import func_logger
from telegrambot.exceptions import HTTPError, TokenError
from telegrambot.utils import extract_address

ENDPOINT = 'https://search-maps.yandex.ru/v1/'
RETRY_PERIOD = 100
YA_TOKEN = os.getenv('YA_TOKEN')
HEADERS = {'apikey': f'{YA_TOKEN}'}
MAX_RESULTS_PER_CITY = 1000
FIRST_RESULT = 1
MESSAGE_ERROR_REQUEST = 'Какие то проблемы с endpoint'
# places for search in API
PLACES = (
    'Кафе',
    'Бар',
    'Паб',
    'Ресторан',
    'Пиццерия',
    'Суши',
    'Баня',
    'Сауна',
)
# Change here `city` to adding to base.
CITIES = (
    'Орел',
    'Курск',
    'Москва',
    'Суджа',
    'Белгород',
    'Болхов',
    'Мценск',
    'Петрозаводск',
)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(funcName)s',
)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('my_logger.log', maxBytes=5000000, backupCount=3)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s, %(funcName)s',
)
handler.setFormatter(formatter)


def check_tokens() -> None:
    """Availability of tokens in environment variables.

    Raises:
        TokenError: Any of the required tokens is missing.

    """
    if not YA_TOKEN:
        logger.critical('Необходимый токен: %s не обнаружен', 'YA_TOKEN')
        raise TokenError('YA_TOKEN')


def get_city(city: str) -> str:
    """Gets the region of the city by its coordinates of its center.

    Args:
        city: Name of city to find them box location

    Returns:
        Coordinates of the lower left and upper right corners of the city
        region

    Raises:
        HTTPError: If Endpoint is unavailable.

    """
    try:
        response = requests.get(
            ENDPOINT,
            params={
                'text': f"{city}",
                'results': FIRST_RESULT,
                'apikey': YA_TOKEN,
                'lang': 'ru',
                'type': 'geo',
            },
        )
    except requests.RequestException as error:
        logging.exception(MESSAGE_ERROR_REQUEST)
        raise HTTPError from error
    if response.status_code != HTTPStatus.OK:
        logger.error(MESSAGE_ERROR_REQUEST)
        raise HTTPError

    coordinates = response.json()['features'][0]['geometry']['coordinates']
    bounded_result = list(
        chain.from_iterable(
            response.json()['properties']['ResponseMetaData'][
                'SearchResponse'
            ]['boundedBy'],
        ),
    )
    try:
        City.objects.create(
            name=city,
            latitude=coordinates[0],
            longitude=coordinates[1],
        )
    except IntegrityError:
        logger.warning('Город уже добавлен в базу данных')

    return (
        f'{bounded_result[0]},{bounded_result[1]}~'
        f'{bounded_result[2]},{bounded_result[3]}'
    )


@func_logger('Получение ответа API')
def get_api_answer(
    max_results: int,
    city: str,
    category: str,
) -> dict:
    """Получаем ответ от эндпоинта.

    Args:
        max_results: Maximum of results in get answer.
        city: City for filtering in question.
        category: Category of place (Bar, restaurant, cafe etc.).

    Returns:
        Response in json form with all Places after filtering.

    Raises:
        HTTPError: If endpoint is unavailable.

    Notes:
        `biz` - Parameter that shows that in the output you need to specify
        organizations.
        `bbox` - Parameter limiting the output of city coordinates data
        (lower left - upper right corner)

    """
    try:
        response = requests.get(
            ENDPOINT,
            params={
                'text': category,
                'results': max_results,
                'apikey': YA_TOKEN,
                'lang': 'ru',
                'type': 'biz',
                'bbox': get_city(city),
            },
        )
    except requests.RequestException as error:
        logging.exception(MESSAGE_ERROR_REQUEST)
        raise HTTPError from error

    if response.status_code != HTTPStatus.OK:
        logger.error(MESSAGE_ERROR_REQUEST)
        raise HTTPError
    return response.json().get('features')


def parser(city: str, category: str) -> None:
    """Processes API request.

    Pull the necessary data and put them in the database.

    Args:
        category: Category of place (Bar, restaurant, cafe etc.).
        city: City for filtering in question.

    """
    place = dict()
    for obj in get_api_answer(
        MAX_RESULTS_PER_CITY,
        city,
        category,
    ):
        place['longitude'] = obj['geometry']['coordinates'][0]
        place['latitude'] = obj['geometry']['coordinates'][1]
        try:
            category_names = [
                key.get('name')
                for key in obj['properties']['CompanyMetaData']['Categories']
            ]
            categories = [
                Category.objects.get_or_create(name=name)[0]
                for name in category_names
            ]
        except KeyError:
            _category, _ = Category.objects.get_or_create(name='Неизвестно')
            categories = [
                _category,
            ]
        except IntegrityError:
            logger.debug('Такой тип заведения уже добавлен')

        try:
            place['name'] = obj['properties']['CompanyMetaData']['name']
            place['address'] = extract_address(
                obj['properties']['description'],
            )
        except KeyError as error:
            logger.debug(f'Отсутствует ключ {error} в API')

        try:
            place['city_id'] = City.objects.get(name=city).pk
        except IntegrityError:
            place['city_id'] = 99999
        except KeyError as error:
            logger.debug(f'Отсутствует ключ {error} в API')

        try:
            place['phone'] = obj['properties']['CompanyMetaData']['Phones'][0][
                'formatted'
            ]
        except KeyError as error:
            logger.debug(f'Отсутствует ключ {error} в API')
            place['phone'] = 'Номер отсутствует'

        try:
            place['url'] = obj['properties']['CompanyMetaData']['url']
        except KeyError:
            place['url'] = 'ссылка отсутствует'

        try:
            place['worktime_from'] = obj['properties']['CompanyMetaData'][
                'Hours'
            ]['Availabilities'][0]['Intervals'][0]['from']
            place['worktime_to'] = obj['properties']['CompanyMetaData'][
                'Hours'
            ]['Availabilities'][0]['Intervals'][0]['to']
        except KeyError:
            place['worktime_from'] = parse_time('00:00:01')
            place['worktime_to'] = parse_time('23:59:59')

        try:
            place_obj, _ = Place.objects.get_or_create(**place)
        except IntegrityError:
            logger.debug('Заведение было создано ранее')
        try:
            [
                CategoryPlace.objects.get_or_create(
                    place=place_obj,
                    category=category,
                )
                for category in categories
            ]
        except IntegrityError:
            logger.debug('Отношение уже было создано')


class Command(BaseCommand):
    def handle(self, *args, **options):
        check_tokens()
        for city in CITIES:
            time.sleep(0.2)
            for place in PLACES:
                time.sleep(0.2)
                parser(city, place)
        logger.info('Импорт завершен успешно!')
