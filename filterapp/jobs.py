from logger.log_config import BOT_LOG
from tgbot.bot.senders import send_messages_return_ids


class PlanBroadcast:
    def __init__(self, msg_bot, users, message):
        self.msg_bot = msg_bot
        self.users = users
        self.message = message

    def __call__(self, *args, **kwargs):
        text = (
            self.message.get("text")
            if self.message.get("text")
            else self.message.get("caption")
        )
        msg_start = text[:30].replace("\n", " ") if text else "<None>"
        BOT_LOG.info(
            f"Broadcast to {len(self.users)} users triggered, message start: "
            f'"{msg_start}"'
        )

        for user in self.users:
            send_messages_return_ids(
                self.message,
                user.user_id,
                self.msg_bot,
            )
