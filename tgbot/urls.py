from django.urls import path
from django.views.decorators.csrf import csrf_exempt

import tgbot.views as wh_views

app_name = "tgbot"

urlpatterns = [
    # TODO: make webhook more secure
    path("", wh_views.index, name="index"),
    path("<int:bot_id>", csrf_exempt(wh_views.TelegramBotWebhookView.as_view())),
]
