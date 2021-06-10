from django.urls import path

import adminapp.views as adminapp

app_name = "adminapp"

urlpatterns = [
    path("logs/", adminapp.logs_list_view, name="log_view"),
]
