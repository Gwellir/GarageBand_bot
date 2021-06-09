class UserIsBannedError(Exception):
    """Возникает, когда приходит сообщение от забаненного пользователя."""

    def __init__(self, user):
        super().__init__(f"Пользователь {user} находится в бане!")


class AdminActionError(Exception):
    """Базовый класс для исключений в работе админки бота"""

    pass


class NoUserWithThisIdError(AdminActionError):
    """Возникает при попытке произвести действие c пользователем с несуществующим ID"""

    def __init__(self, pk):
        super().__init__(f"Пользователь c pk '{pk}' не существует!")


class UserIsNotAdminError(AdminActionError):
    """Возникает при попытке произвести действие c пользователем с несуществующим ID"""

    def __init__(self, user_id):
        super().__init__("Аккаунт не является администраторским!")


class UnknownAdminCommandError(AdminActionError):
    """Возникает, когда в коллбеке приходит неизвестная админская команда."""

    def __init__(self, command, key):
        super().__init__(f"Команда '{command}' с ключом {key} не распознана!")


class MessageDoesNotExistError(AdminActionError):
    """Возникает, при попытке удалить несуществующее сообщение из канала."""

    def __init__(self, message_id):
        super().__init__(f"Сообщение #{message_id} не существует!")


class BotProcessingError(Exception):
    """Базовый класс для исключений в обработке данных в боте"""

    pass


class TextNotProvidedError(BotProcessingError):
    """Возникает, когда пользователь отсылает не текст в ответ на запрос ввода"""

    # обычно происходит, когда при запросе текста передаётся изображение или стикер
    def __init__(self):
        super().__init__("Запрошенный текст не введён!")


class TagDoesNotExist(BotProcessingError):
    """Возникает, когда пользователь вводит неправильное имя тага"""

    def __init__(self, name):
        super().__init__(f"Таг {name} не существует!")


class CallbackNotProvidedError(BotProcessingError):
    """Возникает, когда пользователь отправляет сообщение вместо нажатия кнопки"""

    # происходит, когда на стадии запроса нажатия кнопки передаётся сообщение
    def __init__(self):
        super().__init__("Ожидается нажатие на кнопку!")


class ImageNotProvidedError(BotProcessingError):
    """Возникает, когда пользователь отсылает что-то иное вместо изображения"""

    def __init__(self):
        super().__init__(
            "Запрошенное изображение не загружено!\n"
            "_Возможно, при загрузке не выставлена галочка сжатия._"
        )


class PhoneNumberMalformedError(BotProcessingError):
    """Возникает, когда пользователь вводит странный телефонный номер"""

    def __init__(self):
        super().__init__(
            "Введён неправильный номер телефона, повторите попытку ещё раз!"
        )


class TextTooLongError(BotProcessingError):
    """Возникает, когда пользователь вводит слишком длинный текст в текстовом ответе"""

    def __init__(self, max_length, length):
        super().__init__(
            f"Превышена максимальная длина ответа ({max_length}), сейчас: {length}"
        )


class TextTooShortError(BotProcessingError):
    """Возникает, когда пользователь вводит слишком короткий текст в текстовом ответе"""

    def __init__(self, min_length, length):
        super().__init__(
            f"Слишком короткий ответ, введите не менее {min_length} символов!"
        )


class CallbackExpiredError(BotProcessingError):
    """Возникает, когда пользователь нажимает на кнопку от старого сообщения"""

    def __init__(self, command, user_id):
        super().__init__(
            f"Нажата кнопка в старом сообщении!"
            f"Пользователь: {user_id}, команда: {command}"
        )
