import platform

from telegram import ParseMode
from telegram.ext import Updater
from telegram.ext import messagequeue as mq
from telegram.utils.request import Request

from garage_band_bot.settings import DEBUG
from logger.log_config import BOT_LOG
from tgbot.bot.queue_bot import MQBot

tg_updaters = {}


def run_polling():
    """Запуск в режиме polling

    В соответствии с набором параметров ботов из таблицы MessengerBot создаются
    инстансы PTB MQBot, модифицированные для работы с очередью отправки сообщений (q).

    Соответствующие апдейтеры помещаются в глобальный словарь tg_updaters"""

    from tgbot.bot.dispatcher import setup_dispatcher
    from tgbot.models import MessengerBot

    updaters = []
    global tg_updaters

    q = mq.MessageQueue()
    request = Request(con_pool_size=8)

    for bot in MessengerBot.objects.filter(
        is_active=True, is_debug=DEBUG
    ).select_related():
        token = bot.telegram_instance.token

        tg_bot = MQBot(token, request=request, mqueue=q)
        updater = Updater(bot=tg_bot, use_context=True)
        tg_updaters[token] = updater

        # запуск действий по расписанию для соответствующей модели
        bot.get_bound_model().setup_jobs(updater.job_queue)

        dp = updater.dispatcher
        dp = setup_dispatcher(dp)

        # кросс-ссылки для удобного доступа к очереди и боту изнутри этапа обработки
        # принятых сообщений помещаются в bot_data соответствующего диспетчера
        dp.bot_data["msg_bot"] = bot
        dp.bot_data["job_queue"] = updater.job_queue

        bot_info = tg_bot.get_me()
        bot_link = f"https://t.me/{bot_info['username']}"

        BOT_LOG.info(f"Polling of '{bot_link}' started")

        updater.bot.send_message(
            chat_id=bot.telegram_instance.admin_group_id,
            text=f"Бот перезапущен 😉\n<b>{platform.system()} @ {platform.node()}</b>",
            parse_mode=ParseMode.HTML,
        )

        # инициализация опроса серверов TG
        updater.start_polling()
        updaters.append(updater)
    # for updater in updaters:
    #     updater.idle()
