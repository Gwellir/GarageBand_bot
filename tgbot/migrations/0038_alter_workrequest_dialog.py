# Generated by Django 3.2.3 on 2021-07-19 16:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('convoapp', '0007_alter_message_stage'),
        ('tgbot', '0036_move_stage_info_20210717_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workrequest',
            name='dialog',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bound_request', to='convoapp.dialog'),
        ),
    ]
