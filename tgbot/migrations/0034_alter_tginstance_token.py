# Generated by Django 3.2.3 on 2021-07-16 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0033_alter_workrequest_dialog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tginstance',
            name='token',
            field=models.CharField(db_index=True, max_length=50, verbose_name='Токен ТГ'),
        ),
    ]
