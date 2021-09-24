# Generated by Django 3.2.3 on 2021-09-23 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filterapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bazaarfilter',
            name='high_price',
            field=models.PositiveIntegerField(null=True, verbose_name='Верхний предел цены'),
        ),
        migrations.AddField(
            model_name='bazaarfilter',
            name='low_price',
            field=models.PositiveIntegerField(null=True, verbose_name='Нижний предел цены'),
        ),
    ]
