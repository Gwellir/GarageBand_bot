# Generated by Django 3.2.3 on 2021-06-28 16:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0027_auto_20210628_1932'),
        ('convoapp', '0002_auto_20210628_1932'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='dialog',
        ),
        migrations.DeleteModel(
            name='Dialog',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]