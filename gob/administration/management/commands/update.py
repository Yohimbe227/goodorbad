"""
Fills out or updates the database of institutions.
It uses the yandex API. Thank them very much for providing access.
"""
import logging
import os
import time
from http import HTTPStatus
from itertools import chain

from django.core.management import BaseCommand
from django.db import IntegrityError

import requests

from administration.models import Category, City, Place
from telegrambot.costants import CITY_ID, RUBRIC_ID
from telegrambot.decorators import func_logger
from telegrambot.exceptions import HTTPError
from telegrambot.utils import convert_time, extract_address, extract_city

ENDPOINT = 'https://search-maps.yandex.ru/v1/'
RETRY_PERIOD = 100
YA_TOKEN = os.getenv('YA_TOKEN')
HEADERS = {'apikey': f'{YA_TOKEN}'}
MESSAGE_ERROR_REQUEST = 'Какие то проблемы с endpoint'
PLACES = ('Кафе', 'Бар', 'Паб', 'Ресторан', 'Пиццерия', 'Суши')
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


def get_city(city: str) -> str:
    try:
        response = requests.get(
            ENDPOINT,
            params={
                'text': f"{city}",
                'results': 1,
                'apikey': '0ad0e0b7-de24-4f85-a612-bf45865c8f00',
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
    bounded = response.json()['properties']['ResponseMetaData'][
        'SearchResponse'
    ]['boundedBy']
    bounded_result = list(chain.from_iterable(bounded))
    try:
        City.objects.create(
            name=city, latitude=coordinates[0], longitude=coordinates[1]
        )
    except IntegrityError:
        logger.warning('Город уже добавлен в базу данных')

    return f'{bounded_result[0]},{bounded_result[1]}~{bounded_result[2]},{bounded_result[3]}'


@func_logger('Получение ответа API')
def get_api_answer(
        number_of_results: int,
        city: str,
        category: str,
) -> dict:
    """Получаем ответ от эндпоинта."""

    try:
        response = requests.get(
            ENDPOINT,
            params={
                'text': category,
                'results': number_of_results,
                'apikey': '0ad0e0b7-de24-4f85-a612-bf45865c8f00',
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
    """Обрабатывает запрос к API.

    Вытаскиваем нужные данные и кладем их базу данных.

    Args:
        number_of_pages: number of pages API responce.
        city: city to request.

    """
    place = dict()
    places = []
    for obj in get_api_answer(
            200,
            city,
            category,
    ):
        place['latitude'] = obj['geometry']['coordinates'][0]
        place['longitude'] = obj['geometry']['coordinates'][1]
        try:
            _category_list = obj['properties']['CompanyMetaData']['Categories']
            category_names = [key.get('name') for key in _category_list]
        except KeyError:
            _categoryies = Category(name='Неизвестно')
        try:
            _categoryies = [Category(name=name) for name in category_names]
        except IntegrityError:
            logger.info('Такой тип заведения уже добавлен')
        try:
            place['name'] = obj['properties']['CompanyMetaData']['name']
            place['address'] = extract_address(
                obj['properties']['description']
            )
        except KeyError as error:
            logger.info(f'Отсутствует ключ {error} в API')
        try:
            place['city_id'] = City.objects.get(name=city).pk
        except IntegrityError:
            place['city_id'] = 9999
        except KeyError as error:
            logger.info(f'Отсутствует ключ {error} в API')
        try:
            place['phone'] = obj['properties']['CompanyMetaData'][
                'Phones'
            ][0]['formatted']
        except KeyError as error:
            logger.info(f'Отсутствует ключ {error} в API')
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
            place['worktime_from'] = '00:00:00'
            place['worktime_to'] = '00:00:01'
        places.append(Place(**place))
    Place.objects.bulk_create(places, ignore_conflicts=True)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # try:
            # Change here `city` and `number of pages` to adding to base.
        for city in CITIES:
            time.sleep(0.4)
            for place in PLACES:
                time.sleep(0.1)
                parser(city, place)

        # except AttributeError:
        #     logger.info('The Places was ended, or this is demo restrictions')
