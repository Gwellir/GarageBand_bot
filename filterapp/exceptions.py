from tgbot.exceptions import BotProcessingError


class NotSubscribedError(BotProcessingError):
    """Возникает, когда пользователь не подписан на платную услугу, которой пытается воспользоваться"""

    def __init__(self):
        super(NotSubscribedError, self).__init__(f"Вы не подписаны на данную услугу!")
