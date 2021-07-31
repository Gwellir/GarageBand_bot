# Generated by Django 3.2.3 on 2021-07-19 16:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('convoapp', '0007_alter_message_stage'),
        ('tgbot', '0036_move_stage_info_20210717_1836'),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('short_name', models.CharField(max_length=20, verbose_name='Краткое наименование')),
            ],
        ),
        migrations.CreateModel(
            name='SaleAdStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=50, verbose_name='Наименование')),
                ('processor', models.CharField(max_length=50, null=True, verbose_name='Процессор обработки')),
                ('reply_pattern', models.TextField(verbose_name='Шаблон ответа')),
                ('buttons', models.JSONField(verbose_name='Набор кнопок')),
            ],
        ),
        migrations.CreateModel(
            name='SaleAd',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exact_price', models.CharField(max_length=30, verbose_name='Цена')),
                ('mileage', models.PositiveIntegerField(verbose_name='Пробег')),
                ('description', models.TextField(blank=True, max_length=700, verbose_name='Подробное описание')),
                ('formed_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время составления')),
                ('location', models.CharField(blank=True, max_length=100, verbose_name='Местоположение для ремонта')),
                ('car_type', models.CharField(blank=True, max_length=50, verbose_name='Тип автомобиля')),
                ('is_complete', models.BooleanField(db_index=True, default=False, verbose_name='Флаг готовности заявки')),
                ('is_discarded', models.BooleanField(db_index=True, default=False, verbose_name='Флаг отказа от проведения заявки')),
                ('dialog', models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bound_ad', to='convoapp.dialog')),
                ('price_tag', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='bazaarapp.pricetag')),
                ('stage', models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.SET_NULL, to='bazaarapp.saleadstage')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ads', to='tgbot.botuser')),
            ],
        ),
    ]
