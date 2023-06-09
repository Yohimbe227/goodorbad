import logging
from functools import wraps

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s, %(levelname)s, %(message)s',
)
logger = logging.getLogger(__name__)


def only_one(func):
    @wraps(func)
    def wrapper(*args):
        if wrapper.count == 0:
            wrapper.num = func(*args)
            wrapper.count += 1
            return wrapper.num
        return wrapper.num

    wrapper.count = 0
    return wrapper


def func_logger(message: str, level: str = 'debug'):
    """Декоратор для логирования функции.

    Args:
        message: Message on function execute.
        level: Допустимые значения: 'info', 'debug', 'error', 'critical'.

    Returns:
        Объект функции `_func_logger`

    Raises:
        NameError: При недокументированном уровне логирования.

    """

    def _func_logger(function):
        @wraps(function)
        def wrapper(*args2, **kwargs):
            ret = function(*args2, **kwargs)
            log_level = {
                'debug': logger.debug,
                'info': logger.info,
                'error': logger.error,
                'critical': logger.critical,
            }
            if level in log_level:
                log_level.get(level)(message)
            else:
                raise NameError(f'Unknown parameter {level}')
            return ret

        return wrapper

    return _func_logger
