# Generated by Django 3.2.3 on 2021-07-17 13:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0034_alter_tginstance_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkRequestStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=50, verbose_name='Наименование')),
                ('processor', models.CharField(max_length=50, verbose_name='Процессор обработки', null=True)),
                ('reply_pattern', models.TextField(verbose_name='Шаблон ответа')),
                ('buttons', models.JSONField(verbose_name='Набор кнопок')),
            ],
        ),
        migrations.AddField(
            model_name='workrequest',
            name='stage',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='tgbot.workrequeststage'),
        ),
    ]
