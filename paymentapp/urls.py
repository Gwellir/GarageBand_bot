from django.urls import path

import paymentapp.views

app_name = "convoapp"

urlpatterns = [
    path(
        "callback/",
        paymentapp.views.LiqPayCallbackView.as_view(),
        name="payment_callback",
    ),
]
