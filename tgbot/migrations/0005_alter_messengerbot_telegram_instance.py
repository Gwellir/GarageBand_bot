# Generated by Django 3.2.3 on 2021-08-21 13:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0004_auto_20210818_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messengerbot',
            name='telegram_instance',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bot', to='tgbot.tginstance'),
        ),
    ]
