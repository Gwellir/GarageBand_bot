# Generated by Django 3.2.3 on 2021-09-06 13:23

from django.db import migrations, models
import django.db.models.deletion
from django.db.models import OuterRef, Subquery


def set_location_key(apps, schema_editor):
    SaleAd = apps.get_model("bazaarapp", "SaleAd")
    Location = apps.get_model("tgbot", "location")
    location_names = [entry.name for entry in Location.objects.all()]
    db_alias = schema_editor.connection.alias
    loc = Location.objects.using(db_alias).filter(
        name=OuterRef('location_desc')
    ).values_list(
        'pk'
    )[:1]
    SaleAd.objects.using(db_alias)\
        .filter(location_desc__in=location_names)\
        .update(location_key=Subquery(loc))


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0006_location_region'),
        ('bazaarapp', '0006_location_region_squashed_0008_auto_20210906_1355'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salead',
            old_name='location',
            new_name='location_desc',
        ),
        migrations.AddField(
            model_name='salead',
            name='location_key',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale_ads', to='tgbot.location'),
        ),
        migrations.RunPython(
            set_location_key, migrations.RunPython.noop
        ),
    ]