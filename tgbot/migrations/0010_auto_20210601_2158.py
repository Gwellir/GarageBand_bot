# Generated by Django 3.2.3 on 2021-06-01 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0009_alter_workrequest_dialog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='botuser',
            name='location',
            field=models.CharField(max_length=100, null=True, verbose_name='Указанное местоположение'),
        ),
        migrations.AlterField(
            model_name='botuser',
            name='name',
            field=models.CharField(blank=True, max_length=70, verbose_name='Полное имя для бота'),
        ),
        migrations.AlterField(
            model_name='botuser',
            name='username',
            field=models.CharField(max_length=50, null=True, verbose_name='Ник в ТГ'),
        ),
        migrations.AlterField(
            model_name='workrequest',
            name='description',
            field=models.TextField(blank=True, max_length=700, verbose_name='Подробное описание'),
        ),
        migrations.AlterField(
            model_name='workrequest',
            name='location',
            field=models.CharField(blank=True, max_length=100, verbose_name='Местоположение для ремонта'),
        ),
        migrations.AlterField(
            model_name='workrequest',
            name='phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Номер телефона'),
        ),
        migrations.AlterField(
            model_name='workrequest',
            name='title',
            field=models.CharField(blank=True, max_length=50, verbose_name='Наименование задачи'),
        ),
    ]
