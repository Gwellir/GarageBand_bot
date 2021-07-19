# Generated by Django 3.2.3 on 2021-06-28 16:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0035_auto_20210717_1619'),
    ]

    operations = [
        migrations.RunSQL("""
            UPDATE tgbot_workrequest AS tw
                SET stage_id = (
                    SELECT stage
                        FROM convoapp_dialog AS cd
                        WHERE cd.id = tw.dialog_id
                );

        """, reverse_sql="""
            UPDATE convoapp_dialog AS cd
                SET stage = (
                    SELECT stage_id 
                        FROM tgbot_workrequest AS tw
                        WHERE tw.dialog_id = cd.id
                );
        """)
    ]