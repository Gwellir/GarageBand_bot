from django.urls import path

import convoapp.views

app_name = "convoapp"

urlpatterns = [
    path("logs/", convoapp.views.logs_list_view, name="log_view"),
    path("logs/<int:user_pk>/", convoapp.views.logs_list_view, name="log_view_by_user"),
    path(
        "logs/<int:user_pk>/<int:dialog_pk>/",
        convoapp.views.logs_list_view,
        name="log_view_by_dialog",
    ),
]
