# Generated by Django 3.2.3 on 2021-05-22 14:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Наименование задачи')),
                ('description', models.TextField(blank=True, verbose_name='Подробное описание')),
                ('formed_at', models.DateTimeField(auto_now=True, verbose_name='Время составления')),
                ('location', models.CharField(blank=True, max_length=200, verbose_name='Местоположение для ремонта')),
                ('phone', models.CharField(blank=True, max_length=50, verbose_name='Номер телефона')),
            ],
        ),
        migrations.AlterField(
            model_name='botuser',
            name='dialog_stage',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Стадия 1. Приветствие'), (2, 'Стадия 2. Подтвердить создание заявки'), (3, 'Стадия 3. Получить имя'), (4, 'Стадия 4. Получить название заявки')], default=1, verbose_name='Состояние диалога'),
        ),
        migrations.CreateModel(
            name='RequestPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=255, verbose_name='Описание фото')),
                ('image', models.ImageField(upload_to='', verbose_name='Фотография')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='tgbot.request')),
            ],
        ),
        migrations.AddField(
            model_name='request',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tgbot.botuser'),
        ),
    ]
