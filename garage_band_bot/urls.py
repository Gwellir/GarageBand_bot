"""garage_band_bot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from convoapp import urls as convo_urls
from paymentapp import urls as payment_urls
from statsapp import urls as stats_urls
from tgbot import urls as webhook_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("log_viewer/", include(convo_urls, namespace="log_view")),
    path("stats/", include(stats_urls, namespace="stats")),
    path("_catchers/", include(webhook_urls, namespace="webhooks")),
    path("_payments/", include(payment_urls, namespace="payments")),
]
