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


@func_logger('Получение ответа API')
def get_api_answer(number_of_pages: int) -> dict:
    """Получаем ответ от эндпоинта."""

    try:
        response = requests.get(
            ENDPOINT,
            # headers=HEADERS,
            params={'key': 'ruwnof3076', 'q': 'Орел бар', 'type': 'branch',
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

NEEDED_KEY = ('address_name', 'name',)
CONVERT_API_NAME_TO_MODELS = {
    'name': 'name',

    'address_name': 'address_name',
}


class Command(BaseCommand):

    def handle(self, *args, **options):

        place_item = []
        place = {}
        for page in range(1, 3):
            data_places = get_api_answer(page)
            sleep(0.5)
            for place_source in data_places:
                place_types = []
                for key in place_source.keys():
                    match key:
                        case 'point':
                            place['latitude'] = place_source['point']['lat']
                            place['longitude'] = place_source['point']['lon']
                        case 'rubrics':
                            for rubrics_keys in place_source['rubrics']:

                                place_types.append(PlaceType.objects.create(
                                    name=rubrics_keys['name']))
                        case 'schedule':
                            place['worktime_from'] = convert_time(place_source['schedule']['Fri']['working_hours'][0]['from'])
                            place['worktime_to'] = convert_time(place_source['schedule']['Fri']['working_hours'][0]['to'])
                        case _:
                            place['name'] = place_source['name']
                            place['address_name'] = place_source[
                                'address_name']
                print(place)
                try:
                    Place.objects.create(**place).place_type.add(*place_types)
                except IntegrityError as error:
                    logger.info('Place was added previously')
                # Pl.place_type.add(*place_types)

                # place_item.append(*copy(place))

            # print(place_item)
