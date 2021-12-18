from django.urls import path

import statsapp.views

app_name = "statsapp"

urlpatterns = [
    path("main/", statsapp.views.stats_main, name="stats_main"),
    # path("logs/<int:user_pk>/", statsapp.views.logs_list_view, name="log_view_by_user"),
    # path(
    #     "logs/<int:user_pk>/<int:dialog_pk>/",
    #     statsapp.views.logs_list_view,
    #     name="log_view_by_dialog",
    # ),
]
