from django.contrib import admin

from .models import BotUser, Dialog, RegisteredRequest, RequestPhoto, WorkRequest

# todo rework admin interface to answer project's needs
admin.site.register(BotUser)
admin.site.register(RequestPhoto)
admin.site.register(WorkRequest)
admin.site.register(RegisteredRequest)
admin.site.register(Dialog)
