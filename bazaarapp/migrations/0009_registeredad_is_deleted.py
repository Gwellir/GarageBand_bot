# Generated by Django 3.2.3 on 2021-09-08 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bazaarapp', '0008_auto_20210906_1820'),
    ]

    operations = [
        migrations.AddField(
            model_name='registeredad',
            name='is_deleted',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Сообщение удалено из канала'),
        ),
    ]
