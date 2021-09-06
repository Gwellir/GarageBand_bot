# Generated by Django 3.2.3 on 2021-09-06 15:20
import re

from django.db import migrations, models
from django.db.models import F


class DelBazaarStage:

    def __init__(self, stage_id):
        self.stage_id = stage_id

    def __call__(self, apps, schema_editor):
        SaleAd = apps.get_model("bazaarapp", "SaleAd")
        SaleAdStage = apps.get_model("bazaarapp", "SaleAdStage")
        db_alias = schema_editor.connection.alias
        last_id = SaleAdStage.objects.count()
        SaleAd.objects.using(db_alias).filter(stage_id=self.stage_id).update(stage_id=F('stage_id') + 1)
        SaleAdStage.objects.using(db_alias).filter(id=self.stage_id).delete()
        for sas in SaleAdStage.objects.using(db_alias).filter(id__gte=self.stage_id).order_by('id'):
            sas.id -= 1
            sas.save()
        SaleAdStage.objects.using(db_alias).filter(id=last_id).delete()
        SaleAd.objects.using(db_alias).filter(stage_id__gt=self.stage_id).update(stage_id=F('stage_id') - 1)


class AddBazaarStage:

    def __init__(self, stage_id, name, processor):
        self.stage_id = stage_id
        self.name = name
        self.processor = processor

    def __call__(self, apps, schema_editor):
        SaleAd = apps.get_model("bazaarapp", "SaleAd")
        SaleAdStage = apps.get_model("bazaarapp", "SaleAdStage")
        db_alias = schema_editor.connection.alias
        for sas in SaleAdStage.objects.using(db_alias).filter(id__gte=self.stage_id).order_by('-id'):
            sas.id += 1
            sas.save()
        SaleAdStage.objects.using(db_alias).filter(id=self.stage_id).delete()
        SaleAdStage.objects.using(db_alias).create(id=self.stage_id, name=self.name, processor=self.processor)
        SaleAd.objects.using(db_alias).filter(stage_id__gte=self.stage_id).update(stage_id=F('stage_id') + 1)


def set_low_high(apps, schema_editor):
    PriceTag = apps.get_model("bazaarapp", "PriceTag")
    db_alias = schema_editor.connection.alias
    for tag in PriceTag.objects.using(db_alias).all():
        res = re.findall(r"от(\d+)", tag.short_name)
        if res:
            tag.low = res[0]
        res = re.findall(r"до(\d+)", tag.short_name)
        if res:
            tag.high = res[0]
        tag.save()


class Migration(migrations.Migration):

    dependencies = [
        ('bazaarapp', '0007_auto_20210906_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricetag',
            name='high',
            field=models.PositiveIntegerField(null=True, verbose_name='Верхняя граница цены'),
        ),
        migrations.AddField(
            model_name='pricetag',
            name='low',
            field=models.PositiveIntegerField(null=True, verbose_name='Нижняя граница цены'),
        ),
        migrations.RunPython(
            DelBazaarStage(6), AddBazaarStage(6, 'get_price_tag', 'PriceTagInputProcessor')
        ),
        migrations.RunPython(
            set_low_high, migrations.RunPython.noop
        )
    ]
