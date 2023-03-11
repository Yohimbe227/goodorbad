import logging
import os
from copy import copy
from http import HTTPStatus
from time import sleep

import requests
from django.core.management import BaseCommand
from django.db import IntegrityError

from administration.models import Place, PlaceType
from telegrambot.decorators import func_logger
from telegrambot.exceptions import HTTPError

ENDPOINT = 'https://catalog.api.2gis.com/3.0/items'
RETRY_PERIOD = 100
GIS_TOKEN = os.getenv('GIS_TOKEN')
HEADERS = {'key': f'{GIS_TOKEN}'}
MESSAGE_ERROR_REQUEST = 'Какая то лажа с endpoint'


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(funcName)s',
)
logger = logging.getLogger(__name__)

KEYWORDS = ('бар', 'ресторан', 'кафе', 'пицца')


@func_logger('Получение ответа API')
def get_api_answer(number_of_pages: int, city: str) -> dict:
    """Получаем ответ от эндпоинта."""

    try:
        for keyword in KEYWORDS:
            response = requests.get(
                ENDPOINT,
                # headers=HEADERS,
                params={'key': 'ruwnof3076', 'q': f'{city} {keyword}', 'type': 'branch',
                        'page': number_of_pages,
                        'fields': 'items.point,items.rubrics,items.schedule'},
            )
    except requests.RequestException as err:
        logging.exception(MESSAGE_ERROR_REQUEST)
        raise HTTPError from err

    if response.status_code != HTTPStatus.OK:
        logger.error(MESSAGE_ERROR_REQUEST)
        raise HTTPError
    return response.json().get('result').get('items')


def convert_time(time_work: str) -> str:
    if time_work == '24:00':
        return '00:00'
    return time_work


def parser(number_of_pages: int, city) -> None:
    place = {}
    for page in range(1, number_of_pages):
        sleep(0.1)
        for place_source in get_api_answer(page, city):
            place_types = []
            for key in place_source.keys():
                match key:
                    case 'point':
                        place['latitude'] = place_source['point']['lat']
                        place['longitude'] = place_source['point']['lon']
                    case 'rubrics':
                        for rubrics_keys in place_source['rubrics']:
                            try:
                                place_types.append(PlaceType.objects.create(
                                    name=rubrics_keys['name']))
                            except IntegrityError as error:
                                logger.info('Такой тип заведения уже добавлен')
                                place_types.append(PlaceType.objects.get(name=rubrics_keys['name']))

                    case 'schedule':
                        try:
                            place['worktime_from'] = convert_time(
                                place_source['schedule']['Fri']['working_hours'][
                                    0]['from'])
                            place['worktime_to'] = convert_time(
                                place_source['schedule']['Fri']['working_hours'][
                                    0]['to'])
                        except KeyError as error:
                            logger.info(f'Отсутствует ключ {error} в API')
                    case _:
                        place['name'] = place_source['name']
                        place['address_name'] = place_source[
                            'address_name']

            print(place)
            place['city'] = city
            try:
                Place.objects.create(**place).place_type.add(*place_types)
            except IntegrityError as error:
                logger.info('Place was added previously')


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            parser(9, 'Курск')
        except AttributeError as error:
            logger.info('The Places was ended, or this is demo restrictions')
