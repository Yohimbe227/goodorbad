import os

from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
ID = int(os.getenv('TELEGRAM_TO'))

# Size of city keyboard
NUMBER_OF_ROWS = 2
NUMBER_OF_COLUMNS = 3

PLACE_TYPES = {
    'Бар': (
        'Бары',
        'Бар, паб',
        'Кальян-бар'
    ),
    'Ресторан': (
        'Банкетные залы',
        'Ресторан',
    ),
    'Кафе': (
        'Кафе',
        'Столовые',
        'Железнодорожные вокзалы',
    ),
    'Пицца/Суши': (
        'Пиццерии',
        'Пиццерия',
        'Pizzerias',
        'Суши-бар',
    ),
    'Фастфуд': (
        'Фастфуд',
        'Быстрое питание',
        'Cafe / fast food restaurants',
    ),
    'Баня/Сауна': (
        'Баня',
        'Сауна',
    ),
    'Кофейня': (
        'Кофейня',
        'Пекарня',
    ),
    'Караоке': (
        'Караоке-зал',
        'Караоке-клуб'
    ),
    'Ночной клуб': (
        'Ночной клуб',
        'Стриптиз-клуб',
    ),
}
KEYWORDS = (
    'бар',
    'ресторан',
    'кафе',
)

# id типов заведений по 2 gis (кафе, ресторан, бар и т.п.)
CITY_ID = {
    'Орел': 9992984443486357,
    'Болхов': 70030076127877656,
    'Мценск': 70030076127876527,
    'Суджа': 70030076128107843,
    'Москва': 4504222397630173,
    'Курск': 10274459420196967,
    'Белгород': 6474547234603025,
}

RUBRIC_ID = '164,165,161,21387,15791,15791,159,111594,110530,51459,16677,173'

MAX_QUANTITY_OF_PLACES_ON_KB = 12

M_IN_KM = 1000  # 1000 to become the distance in meter

NUMBER_OF_PLACES_TO_SHOW = 3

START_MESSAGE = (
    'Добро пожаловать {username}. \nИщи кафе, бары, рестораны и'
    ' прочие заведения, находящиеся поблизости. \nЧитай и оставляй '
    'отзывы. \nХорошего отдыха!'
)

BUTTONS_PLACE_TYPE = (
    'Бар',
    'Ресторан',
    'Кафе',
    'Пиццерия',
    'Фастфуд',
    'Суши бар',
    'Кофейня',
    'Караоке',
)

ALPHABET = {
    'а': '[@|а|а́|a]',
    'б': '[б|6|b]',
    'в': '[в|b|v]',
    'г': '[г|r|g]',
    'д': '[д|d]',
    'е': '[е|e|ё]',
    'ж': '[ж|z|*]',
    'з': '[з|3|z]',
    'и': '[и|u|i]',
    'й': '[й|u|i]',
    'к': '[к|k]',
    'л': '[л|l]',
    'м': '[м|m]',
    'н': '[н|h|n]',
    'о': '[о|o|0]',
    'п': '[п|n|p]',
    'р': '[р|r|p]',
    'с': '[с|c|s|5|$]',
    'т': '[т|m|t]',
    'у': '[у́|у|y|u]',
    'ф': '[ф|f]',
    'х': '[х|x|h]',
    'ц': '[ц|c|u]',
    'ч': '[ч|c|h]',
    'ш': '[ш|щ]',
    'ь': '[ь|b]',
    'ы': '[ы|i]',
    'ъ': '[ъ|ь]',
    'э': '[э|e]',
    'ю': '[ю|y|u]',
    'я': '[я|r]',
    ' ': '[.|,|!|?|&|)|(|\\|\/|*|-|_|"|\'|;|®]',
}
