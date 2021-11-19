from django.urls import path

import paymentapp.views

app_name = "convoapp"

urlpatterns = [
    path("callback/", paymentapp.views.PayCallbackView.as_view(), name="payment_callback"),
]

