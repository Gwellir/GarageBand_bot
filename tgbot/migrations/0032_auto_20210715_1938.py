# Generated by Django 3.2.3 on 2021-07-15 16:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0031_messengerbot_tginstance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tginstance',
            name='admin_group_id',
            field=models.BigIntegerField(null=True, verbose_name='Группа администрирования'),
        ),
        migrations.AlterField(
            model_name='tginstance',
            name='discussion_group_id',
            field=models.BigIntegerField(null=True, verbose_name='Группа обсуждения'),
        ),
        migrations.AlterField(
            model_name='tginstance',
            name='feedback_group_id',
            field=models.BigIntegerField(null=True, verbose_name='Группа фидбека'),
        ),
        migrations.AlterField(
            model_name='tginstance',
            name='publish_id',
            field=models.BigIntegerField(verbose_name='Основной канал бота'),
        ),
    ]
