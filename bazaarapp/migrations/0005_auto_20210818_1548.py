# Generated by Django 3.2.3 on 2021-08-18 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bazaarapp', '0004_auto_20210818_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registeredad',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания'),
        ),
        migrations.AlterField(
            model_name='registeredad',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последней активности'),
        ),
        migrations.AlterField(
            model_name='salead',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания'),
        ),
        migrations.AlterField(
            model_name='salead',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последней активности'),
        ),
    ]
