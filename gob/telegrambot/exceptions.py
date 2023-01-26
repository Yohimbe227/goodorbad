class Error(Exception):
    pass


class TokenError(Error):
    def __init__(self, token):
        self.token = token
        super().__init__(f'Отсутствует необходимый токен: {token}')


class HTTPError(Error):
    def __str__(self):
        return f'{type(self).__name__}. Эндпоинт не доступен'


class StatusError(Error):
    def __str__(self):
        return f'{type(self).__name__}. Неожиданный статус домашней работы'


class SendMessageError(Error):
    def __str__(self):
        return 'f{type(self).__name__}. Ошибка отправки сообщения'
