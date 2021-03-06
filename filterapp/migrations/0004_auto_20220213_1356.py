# Generated by Django 3.2.3 on 2022-02-13 10:56
from functools import partial

from django.db import migrations

from utils.migrate import add_foreign_keys, del_foreign_keys


class Migration(migrations.Migration):

    dependencies = [
        ('filterapp', '0003_auto_20211109_1956'),
    ]

    operations = [
        migrations.RunPython(
            partial(
                add_foreign_keys,
                model_name="filterapp.RepairsFilter",
                key_model_name="filterapp.RepairsFilterStage",
                keys=[
                    dict(id=3, name="GET_COMPANY_NAME", processor="CompanyNameInputProcessor"),
                ],
                relation_name="stage",
            ),
            reverse_code=partial(
                del_foreign_keys,
                model_name="filterapp.RepairsFilter",
                key_model_name="filterapp.RepairsFilterStage",
                ids=[3],
                relation_name="stage",
            )
        )
    ]
