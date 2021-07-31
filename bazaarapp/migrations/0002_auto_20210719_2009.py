# Generated by Django 3.2.3 on 2021-07-19 17:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('convoapp', '0007_alter_message_stage'),
        ('bazaarapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salead',
            name='dialog',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bound_salead', to='convoapp.dialog'),
        ),
        migrations.AlterField(
            model_name='salead',
            name='exact_price',
            field=models.CharField(max_length=30, null=True, verbose_name='Цена'),
        ),
        migrations.AlterField(
            model_name='salead',
            name='mileage',
            field=models.PositiveIntegerField(null=True, verbose_name='Пробег'),
        ),
    ]
