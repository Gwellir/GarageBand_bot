from django.urls import path

import adminapp.views as adminapp

app_name = "adminapp"

urlpatterns = [
    path("logs/", adminapp.logs_list_view, name="log_view"),
    path("logs/<int:user_pk>/", adminapp.logs_list_view, name="log_view_by_user"),
    path(
        "logs/<int:user_pk>/<int:dialog_pk>/",
        adminapp.logs_list_view,
        name="log_view_by_dialog",
    ),
]
