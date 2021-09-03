# Generated by Django 3.2.3 on 2021-09-01 13:02

from django.db import migrations, models
import django.db.models.deletion


def fill_stages(apps, schema_editor):
    BFS = apps.get_model("filterapp", "BazaarFilterStage")
    db_alias = schema_editor.connection.alias
    BFS.objects.using(db_alias).bulk_create([
       BFS(name="welcome", processor="StartInputProcessor", reply_pattern="", buttons="{}"),
       BFS(name="get_price_ranges", processor="PriceMultiSelectProcessor", reply_pattern="", buttons="{}"),
       BFS(name="get_regions", processor="RegionMultiSelectProcessor", reply_pattern="", buttons="{}"),
       BFS(name="check_data", processor="SetReadyInputProcessor", reply_pattern="", buttons="{}"),
       BFS(name="done", processor=None, reply_pattern="", buttons="{}"),
    ])


def unmigrate(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bazaarapp', '0007_alter_salead_description'),
        ('tgbot', '0005_alter_messengerbot_telegram_instance'),
        ('convoapp', '0005_auto_20210818_1548'),
    ]

    operations = [
        migrations.CreateModel(
            name='BazaarFilterStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=50, verbose_name='Наименование')),
                ('processor', models.CharField(max_length=50, null=True, verbose_name='Процессор обработки')),
                ('reply_pattern', models.TextField(null=True, verbose_name='Шаблон ответа')),
                ('buttons', models.JSONField(null=True, verbose_name='Набор кнопок')),
            ],
        ),
        migrations.CreateModel(
            name='BazaarFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последней активности')),
                ('is_complete', models.BooleanField(db_index=True, default=False, verbose_name='Флаг готовности фильтра')),
                ('is_discarded', models.BooleanField(db_index=True, default=False, verbose_name='Флаг отказа от формирования фильтра')),
                ('stage', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='filterapp.bazaarfilterstage', default=1)),
                ('dialog', models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bound_bazaarfilter', to='convoapp.dialog')),
                ('price_ranges', models.ManyToManyField(to='bazaarapp.PriceTag', verbose_name='Диапазоны цен')),
                ('regions', models.ManyToManyField(to='bazaarapp.Region', verbose_name='Регионы')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='filters', to='tgbot.botuser', verbose_name='Пользователь')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RegisteredBazaarFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Время создания')),
                ('updated_at', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Время последней активности')),
                ('is_active', models.BooleanField(verbose_name='Фильтр задействован', default=True)),
                ('bound', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='registered', to='filterapp.bazaarfilter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RunPython(fill_stages, unmigrate)
    ]
