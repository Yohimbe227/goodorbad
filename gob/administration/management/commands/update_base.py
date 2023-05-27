"""
Fills out or updates the database of institutions.
It uses the 2gis API. Thank them very much for providing access.
"""
import logging
import os
from http import HTTPStatus

from django.core.management import BaseCommand
from django.db import IntegrityError

import requests

from administration.models import Place, Category
from telegrambot.costants import CITY_ID, RUBRIC_ID
from telegrambot.decorators import func_logger
from telegrambot.exceptions import HTTPError
from telegrambot.utils import convert_time

ENDPOINT = 'https://catalog.api.2gis.com/3.0/items'
RETRY_PERIOD = 100
GIS_TOKEN = os.getenv('GIS_TOKEN')
HEADERS = {'key': f'{GIS_TOKEN}'}
MESSAGE_ERROR_REQUEST = 'Какие то проблемы с endpoint'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(funcName)s',
)
logger = logging.getLogger(__name__)


@func_logger('Получение ответа API')
def get_api_answer(
    number_of_page: int,
    city: str,
) -> dict:
    """Получаем ответ от эндпоинта."""

    try:
        response = requests.get(
            ENDPOINT,
            params={
                'city_id': f'{CITY_ID[city]}',
                'page': number_of_page,
                'page_size': 10,
                'fields': 'items.point,items.rubrics',
                'rubric_id': RUBRIC_ID,
                'key': 'ruwnof3076',
            },
        )
    except requests.RequestException as error:
        logging.exception(MESSAGE_ERROR_REQUEST)
        raise HTTPError from error

    if response.status_code != HTTPStatus.OK:
        logger.error(MESSAGE_ERROR_REQUEST)
        raise HTTPError
    return response.json().get('result').get('items')


def parser(number_of_pages: int, city: str) -> None:
    """Обрабатывает запрос к API.

    Вытаскиваем нужные данные и кладем их базу данных.

    Args:
        number_of_pages: number of pages API responce.
        city: city to request.

    """
    place = {}
    for page in range(1, number_of_pages):  # iteration by pages
        for place_source in get_api_answer(
            page,
            city,
        ):  # iteration by object on page
            place_types = []
            for key in place_source.keys():  # by keys in object
                match key:
                    case 'point':
                        place['latitude'] = place_source['point']['lat']
                        place['longitude'] = place_source['point']['lon']
                    case 'rubrics':
                        for rubrics_keys in place_source['rubrics']:
                            try:
                                place_types.append(
                                    Category.objects.create(
                                        name=rubrics_keys['name'],
                                    ),
                                )
                            except IntegrityError:
                                logger.info('Такой тип заведения уже добавлен')
                                place_types.append(
                                    Category.objects.get(
                                        name=rubrics_keys['name'],
                                    ),
                                )

                    case 'schedule':
                        try:
                            # Тут временный костыль. Время работы берется
                            # только по пятнице!
                            place['worktime_from'] = convert_time(
                                place_source['schedule']['Fri'][
                                    'working_hours'
                                ][0]['from'],
                            )
                            place['worktime_to'] = convert_time(
                                place_source['schedule']['Fri'][
                                    'working_hours'
                                ][0]['to'],
                            )
                        except KeyError as error:
                            logger.info(f'Отсутствует ключ {error} в API')
                    case _:
                        place['name'] = place_source['name']
                        try:
                            place['address_name'] = place_source[
                                'address_name'
                            ]
                        except KeyError as error:
                            logger.error(f'Нет такого ключа {error}')

            place['city'] = city
            try:
                Place.objects.create(**place).category.add(*place_types)
            except IntegrityError:
                logger.info('Place was added previously')


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            # Change here `city` and `number of pages` to adding to base.
            parser(9, 'Орел')
        except AttributeError:
            logger.info('The Places was ended, or this is demo restrictions')
