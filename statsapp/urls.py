from django.urls import path

import statsapp.views

app_name = "statsapp"

urlpatterns = [
    path("main/", statsapp.views.stats_main, name="stats_main"),
]
