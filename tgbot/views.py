import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from tgbot.bot.dispatcher import process_telegram_event
from tgbot.models import MessengerBot


def index(request):
    return JsonResponse({"error": "Y halo thar"})


class TelegramBotWebhookView(View):
    # WARNING: if fail - Telegram webhook will be delivered again.
    # Can be fixed with async celery task execution
    def post(self, request, *args, **kwargs):
        msg_bot = get_object_or_404(MessengerBot, id=self.kwargs['bot_id'])
        dp = msg_bot.telegram_instance.tg_bot
        process_telegram_event(json.loads(request.body), dp)
            # Process Telegram event in Celery worker (async)
            # Don't forget to run it and & Redis (message broker for Celery)!
            # Read Procfile for details
            # You can run all of these services via docker-compose.yml
            # process_telegram_event.delay(json.loads(request.body))

        # TODO: there is a great trick to send action in webhook response
        # e.g. remove buttons, typing event
        return JsonResponse({"ok": "POST request processed"})

    def get(self, request, *args, **kwargs):  # for debug
        return JsonResponse({"ok": "Get request received!"})
