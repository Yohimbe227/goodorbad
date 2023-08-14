class Error(Exception):
    pass


class TokenError(Error):
    def __init__(self, token):
        self.token = token
        super().__init__(f'Отсутствует необходимый токен: {token}')


class TokenQuantityError(Error):
    def __str__(self):
        return f'Все доступные токены кончились'


class HTTPError(Error):
    def __str__(self):
        return f'{type(self).__name__}. Эндпоинт не доступен'


class SendMessageError(Error):
    def __str__(self):
        return f'{type(self).__name__}. Ошибка отправки сообщения'


class UnknownError(Error):
    def __str__(self):
        return f'{type(self).__name__}. Что-то не так с созданием пользователя'


class ReviewBecomeError(Error):
    def __str__(self):
        return (
            f'{type(self).__name__}. Что-то не так с получением отзыва '
            f'из базы'
        )
