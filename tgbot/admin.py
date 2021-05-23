from django.contrib import admin

from .models import BotUser, RequestPhoto, WorkRequest

# Register your models here.
admin.site.register(BotUser)
admin.site.register(RequestPhoto)
admin.site.register(WorkRequest)