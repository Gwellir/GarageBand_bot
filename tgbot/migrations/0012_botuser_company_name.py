# Generated by Django 3.2.3 on 2022-02-13 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0011_alter_botuser_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='company_name',
            field=models.CharField(max_length=255, null=True, verbose_name='Название компании (СТО)'),
        ),
    ]