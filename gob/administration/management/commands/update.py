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
from telegrambot.utils import convert_time, extract_city, extract_address

ENDPOINT = 'https://search-maps.yandex.ru/v1/'
RETRY_PERIOD = 100
YA_TOKEN = os.getenv('YA_TOKEN')
HEADERS = {'apikey': f'{YA_TOKEN}'}
MESSAGE_ERROR_REQUEST = 'Какие то проблемы с endpoint'
CITYES = ('Орел', 'Курск', 'Москва', 'Суджа', 'Белгород', 'Болхов', 'Мценск',)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s, %(funcName)s',
)
logger = logging.getLogger(__name__)


@func_logger('Получение ответа API')
def get_api_answer(
        number_of_results: int,
        city: str,
        type_place: str,
) -> dict:
    """Получаем ответ от эндпоинта."""

    try:
        response = requests.get(
            ENDPOINT,
            params={
                'text': f"{city} {type_place}",
                'results': number_of_results,
                'apikey': '0ad0e0b7-de24-4f85-a612-bf45865c8f00',
                'lang': 'ru',
                'type': 'biz',
            },
        )
    except requests.RequestException as error:
        logging.exception(MESSAGE_ERROR_REQUEST)
        raise HTTPError from error

    if response.status_code != HTTPStatus.OK:
        logger.error(MESSAGE_ERROR_REQUEST)
        raise HTTPError
    return response.json().get('features')


def parser(city: str, type_place: str) -> None:
    """Обрабатывает запрос к API.

    Вытаскиваем нужные данные и кладем их базу данных.

    Args:
        number_of_pages: number of pages API responce.
        city: city to request.

    """
    place = {}
    places = []
    for obj in get_api_answer(
            10,
            type_place,
            city,
    ):
        place['latitude'] = obj['geometry']['coordinates'][0]
        place['longitude'] = obj['geometry']['coordinates'][1]
        _category_list = obj['properties']['CompanyMetaData']['Categories']
        category_names = [key.get('name') for key in _category_list]
        try:
            _categoryies = [Category(name=name) for name in category_names]
        except IntegrityError:
            logger.info('Такой тип заведения уже добавлен')
        # try:
        #     place_types.append(
        #         Category.objects.create(
        #             name=object['properties']['CompanyMetaData']['Categories'],
        #         ),
        #     )
        # except IntegrityError:
        #     logger.info('Такой тип заведения уже добавлен')
        # place_types.append(
        #     PlaceType.objects.get(
        #         name=rubrics_keys['name'],
        #     ),
        # )
        try:
            place['name'] = obj['properties']['CompanyMetaData']['name']
            place['address'] = extract_address(obj['properties']['description'])
            try:
                place['phone'] = obj['properties']['CompanyMetaData']['Phones'][0]['formatted']
            except IndexError:
                place['phone'] = 'номер отутствует'
                logger.warning('Есть заведения без телефонного номера')

            place['worktime_from'] = obj['properties']['CompanyMetaData']['Hours'][
                'Availabilities'][0]['Intervals'][0]['from']
            place['worktime_to'] = obj['properties']['CompanyMetaData']['Hours'][
                'Availabilities'][0]['Intervals'][0]['to']
            place['city'] = extract_city(obj['properties']['description'])
        except KeyError as error:
            logger.info(f'Отсутствует ключ {error} в API')
        places.append(Place(**place))

        print(places)

    #         case 'schedule':
    #             try:
    #                 # Тут временный костыль. Время работы берется
    #                 # только по пятнице!
    #                 place['worktime_from'] = convert_time(
    #                     place_source['schedule']['Fri'][
    #                         'working_hours'
    #                     ][0]['from'],
    #                 )
    #                 place['worktime_to'] = convert_time(
    #                     place_source['schedule']['Fri'][
    #                         'working_hours'
    #                     ][0]['to'],
    #                 )
    #             except KeyError as error:
    #                 logger.info(f'Отсутствует ключ {error} в API')
    #         case _:
    #             place['name'] = place_source['name']
    #             try:
    #                 place['address_name'] = place_source[
    #                     'address_name'
    #                 ]
    #             except KeyError as error:
    #                 logger.error(f'Нет такого ключа {error}')
    #
    # place['city'] = city
    # try:
    #     Place.objects.create(**place).place_type.add(*place_types)
    # except IntegrityError:
    #     logger.info('Place was added previously')


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            # Change here `city` and `number of pages` to adding to base.
            parser('Орел', 'Бар')
        except AttributeError:
            logger.info('The Places was ended, or this is demo restrictions')
