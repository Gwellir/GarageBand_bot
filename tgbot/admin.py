from django.contrib import admin

from convoapp.models import Dialog, Message

from .models import BotUser, RegisteredRequest, RequestPhoto, RepairsType, WorkRequest

# todo rework admin interface to answer project's needs
admin.site.register(BotUser)
admin.site.register(RequestPhoto)
admin.site.register(WorkRequest)
admin.site.register(RegisteredRequest)
admin.site.register(Dialog)
admin.site.register(RepairsType)
admin.site.register(Message)
