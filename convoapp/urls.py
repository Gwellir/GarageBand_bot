from django.urls import re_path

import convoapp.views

app_name = "convoapp"

urlpatterns = [
    re_path(
        r"^logs/(?P<bot>[0-9]+)/(?P<stage>stage-[0-9]+/)?$",
        convoapp.views.logs_list_view,
        name="logs",
    ),
    re_path(
        r"^logs/(?P<bot>[0-9]+)/(?P<stage>stage-[0-9]+/)?(?P<user_pk>[0-9]+)/$",
        convoapp.views.logs_list_view,
        name="logs_by_user",
    ),
    re_path(
        r"^logs/(?P<bot>[0-9]+)/(?P<stage>stage-[0-9]+/)?"
        r"(?P<user_pk>[0-9]+)/(?P<dialog_pk>[0-9]+)/$",
        convoapp.views.logs_list_view,
        name="logs_by_dialog",
    ),
]
