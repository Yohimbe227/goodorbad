"""
Fills out or updates the database of institutions.
It uses the yandex API.
"""
import logging
import os
import time
from copy import copy
from http import HTTPStatus
from itertools import chain
from logging.handlers import RotatingFileHandler

from django.core.management import BaseCommand
from django.db import IntegrityError
from django.utils.dateparse import parse_time

import requests

from administration.models import Category, CategoryPlace, City, Place
from telegrambot.costants import MAX_LENGTH_NAME
from telegrambot.decorators import func_logger
from telegrambot.exceptions import (
    HTTPError,
    TokenError,
    TokenNotValidError,
    TokensIsOutError,
)
from telegrambot.utils import extract_address

ENDPOINT = "https://search-maps.yandex.ru/v1/"
RETRY_PERIOD = 100
YA_TOKENS = os.getenv("YA_TOKEN").split(", ")
YA_GEO_TOKEN = os.getenv("YA_GEO_TOKEN")
MAX_RESULTS_PER_CITY = 1000
FIRST_RESULT = 1
MESSAGE_ERROR_REQUEST = "Какие то проблемы с endpoint"
# places for search in API by default
CATEGORIES = (
    "Кафе",
    "Бар",
    "Паб",
    "Ресторан",
    "Пиццерия",
    "Суши",
    "Баня",
    "Сауна",
)
CITIES = (
    "Нягань",
    "Москва",
    "Санкт-Петербург",
    "Новосибирск",
    "Екатеринбург",
    "Казань",
    "Нижний Новгород",
    "Челябинск",
    "Красноярск",
)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s, %(levelname)s, %(message)s, %(funcName)s",
)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler("my_logger.log", maxBytes=5000000, backupCount=3)
logger.addHandler(handler)
formatter = logging.Formatter(
    "%(asctime)s, %(levelname)s, %(message)s, %(funcName)s",
)
handler.setFormatter(formatter)

test_params = {
    "text": "Москва",
    "results": FIRST_RESULT,
    "apikey": "wrong_token_only_for_test",
    "lang": "ru",
    "type": "geo",
}


def is_token_present() -> None:
    """Availability of tokens in environment variables.

    Raises:
        TokenError: Any of the required tokens is missing.

    """
    if not YA_TOKENS:
        logger.critical("Необходимый токены: %s не обнаружены", "YA_TOKENS")
        raise TokenError("YA_TOKEN")


def is_api_ok():
    test_response = requests.get(
        ENDPOINT,
        params={
            "text": "Москва",
            "results": FIRST_RESULT,
            "apikey": "wrong_token_only_for_test",
            "lang": "ru",
            "type": "geo",
        },
    )
    if test_response.status_code in (HTTPStatus.OK, HTTPStatus.FORBIDDEN):
        return True
    logger.error(MESSAGE_ERROR_REQUEST)
    return False


def is_token_valid(token):
    test_response = requests.get(
        ENDPOINT,
        params={
            "text": "Москва",
            "results": FIRST_RESULT,
            "apikey": token,
            "lang": "ru",
            "type": "geo",
        },
    )
    if test_response.status_code == HTTPStatus.FORBIDDEN:
        logger.error("Токен заблокирован")
        return False
    return True


def get_city(city: str, token: str) -> str:
    """Get the region of the city by coordinates of his center.

    Args:
        city: Name of city to find them box location.

    Returns:
        Coordinates of the lower left and upper right corners of the city
        region.

    Raises:
        TokenNotValidError: If token is not valid.

    """
    if not is_token_valid(token):
        raise TokenNotValidError

    response = requests.get(
        ENDPOINT,
        params={
            "text": f"{city}",
            "results": FIRST_RESULT,
            "apikey": token,
            "lang": "ru",
            "type": "geo",
        },
    )

    coordinates = response.json()["features"][0]["geometry"]["coordinates"]
    bounded_result = list(
        chain.from_iterable(
            response.json()["properties"]["ResponseMetaData"]["SearchResponse"][
                "boundedBy"
            ],
        ),
    )
    try:
        City.objects.get_or_create(
            name=city,
            latitude=coordinates[0],
            longitude=coordinates[1],
            left_box_latitude=bounded_result[0],
            left_box_longitude=bounded_result[1],
            right_box_latitude=bounded_result[2],
            right_box_longitude=bounded_result[3],
        )
    except IntegrityError:
        logger.warning(f"Город {city} уже добавлен в базу данных")
    return (
        f"{bounded_result[0]},{bounded_result[1]}~"
        f"{bounded_result[2]},{bounded_result[3]}"
    )


@func_logger("Получение ответа API")
def get_api_answer(
    max_results: int,
    city: str,
    category: str,
    token: str,
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
        TokenNotValidError: If token is not valid.
    Notes:
        `biz` - Parameter that shows that in the output you need to specify
        organizations.
        `bbox` - Parameter limiting the output of city coordinates data
        (lower left - upper right corner)

    """
    if not is_token_valid(token):
        raise TokenNotValidError("Токен заблокирован")
    if not is_api_ok():
        raise HTTPError("Проблемы  с сетью")

    _city = get_city(city, token)
    response = requests.get(
        ENDPOINT,
        params={
            "text": f"{category} {city}",
            "results": max_results,
            "apikey": token,
            "lang": "ru",
            "type": "biz",
            "bbox": _city,
        },
    )
    return response.json().get("features")


def _parse_from_file(cities: list[str]) -> None:
    """Парсим заведения по городам и категориям из списка.

    Из-за ограничения на количество запросов к API используется список токенов.
    При выходе из строя одного токены, подключается следующий.

    Args:
        cities: Список городов.

    Raises:
        HTTPError: If any troubles with API.
        TokensIsOutError: If valid tokens is out.

    """
    ya_tokens = copy(YA_TOKENS)

    for city in cities:
        for category in CATEGORIES:
            for token in ya_tokens[::-1]:
                if not is_api_ok:
                    raise HTTPError(MESSAGE_ERROR_REQUEST)
                is_valid = is_token_valid(token)
                if not is_valid:
                    ya_tokens.pop()
                    if not ya_tokens:
                        raise TokensIsOutError
                    continue
                parser(city, category, token)
                break
            if is_valid:
                logger.info(
                    f"Все заведения из категории {category} города {city} "
                    f"были добавлены",
                )
        if is_valid:
            logger.info(f"импорт города {city} завершен успешно!")


def parser(city: str, category: str, token: str) -> None:
    """Processes API request.

    Pull the necessary data and put them in the database.

    Args:
        category: Category of place (Bar, restaurant, cafe etc.).
        city: City for filtering in question.
        token: Ya token for API.

    Raises:
        HTTPError: If endpoint is unavailable.
        TokenNotValidError: If token is not valid.

    """
    time.sleep(0.2)
    place = dict()
    if not is_token_valid(token):
        raise TokenNotValidError("Токен заблокирован")
    if not is_api_ok():
        raise HTTPError("Проблемы  с сетью")

    logger.info(f"{token[10:]}")
    api_answer = get_api_answer(
        MAX_RESULTS_PER_CITY,
        city,
        category,
        token,
    )

    for obj in api_answer:
        place["longitude"] = obj["geometry"]["coordinates"][0]
        place["latitude"] = obj["geometry"]["coordinates"][1]
        try:
            category_names = [
                key["name"]
                for key in obj["properties"]["CompanyMetaData"]["Categories"]
            ]
            categories = [
                Category.objects.create(name=name)
                for name in category_names
                if not Category.objects.filter(name=name).exists()
            ]
        except KeyError:
            _category, _ = Category.objects.get_or_create(name="Неизвестно")
            categories = [
                _category,
            ]
        except IntegrityError:
            logger.debug("Такой тип заведения уже добавлен")

        try:
            place["name"] = obj["properties"]["CompanyMetaData"]["name"][
                :MAX_LENGTH_NAME
            ]
            place["address"] = extract_address(
                obj["properties"]["description"],
            )
        except KeyError as error:
            logger.debug(f"Отсутствует ключ {error} в API")

        try:
            place["city_id"] = City.objects.get(name=city).pk
        except IntegrityError:
            place["city_id"] = 99999
        except KeyError as error:
            logger.debug(f"Отсутствует ключ {error} в API")

        try:
            place["phone"] = obj["properties"]["CompanyMetaData"]["Phones"][0][
                "formatted"
            ]
        except KeyError as error:
            logger.debug(f"Отсутствует ключ {error} в API")
            place["phone"] = "Номер отсутствует"

        try:
            place["url"] = obj["properties"]["CompanyMetaData"]["url"]
        except KeyError:
            place["url"] = "ссылка отсутствует"

        try:
            place["worktime_from"] = obj["properties"]["CompanyMetaData"]["Hours"][
                "Availabilities"
            ][0]["Intervals"][0]["from"]
            place["worktime_to"] = obj["properties"]["CompanyMetaData"]["Hours"][
                "Availabilities"
            ][0]["Intervals"][0]["to"]
        except KeyError:
            place["worktime_from"] = parse_time("00:00:01")
            place["worktime_to"] = parse_time("23:59:59")

        try:
            [
                CategoryPlace.objects.get_or_create(
                    place=Place.objects.get_or_create(**place)[0],
                    category=category,
                )
                for category in categories
            ]
        except IntegrityError:
            logger.debug("Отношение уже было создано")


class Command(BaseCommand):
    help = "Команда для записи данных в базу"

    def add_arguments(self, func):
        func.add_argument("--city", type=str, help="Название города")
        func.add_argument("--file", type=str, help="Название файла")

    def handle(self, *args, **options):
        is_token_present()
        city = options["city"]
        file = options["file"]

        if city:
            [parser(city, category, YA_TOKENS[0]) for category in CATEGORIES]
            logger.info(f"Импорт города {city} завершен успешно!")
            return
        elif file and not city:
            file_path = os.path.join("data", file)
            with open(file_path, "r", encoding="utf-8") as file:
                cities = [city.strip() for city in file.readlines()]
                try:
                    _parse_from_file(cities)
                    logger.info(f"Импорт городов {cities} завершен успешно!")
                except HTTPError:
                    logger.critical(MESSAGE_ERROR_REQUEST)
                except TokensIsOutError:
                    logger.critical("Рабочие токены закончились")
        elif not city and not file:
            [
                [parser(city, category, YA_TOKENS[0]) for category in CATEGORIES]
                for city in CITIES
            ]
            logger.info(f"Импорт городов {CITIES} завершен успешно!")
            return
