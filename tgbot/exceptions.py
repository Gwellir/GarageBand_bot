class BotProcessingError(Exception):
    """Базовый класс для исключений в обработке данных в боте"""

    pass


class NoTextProvidedError(BotProcessingError):
    """Возникает, когда пользователь не предоставляет текст в ответ за запрос ввода"""

    # обычно происходит, когда на стадии запроса текста передаётся изображение или стикер
    def __init__(self):
        super().__init__(f"Запрошенный текст не введён")