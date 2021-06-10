# Generated by Django 3.2.3 on 2021-06-09 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0018_auto_20210608_1943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dialog',
            name='stage',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Приветствие'), (2, 'Получить имя'), (3, 'Получить категорию заявки'), (4, 'Получить описание заявки'), (5, 'Предложить отправить фотографии'), (6, 'Получить местоположение'), (7, 'Получить телефон'), (8, 'Проверить заявку'), (9, 'Работа завершена')], default=1, verbose_name='Состояние диалога'),
        ),
    ]