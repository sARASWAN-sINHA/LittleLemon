# Generated by Django 4.2 on 2023-04-23 09:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("LittleLemonAPI", "0005_alter_order_date_alter_order_total"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="date",
            field=models.DateTimeField(
                db_index=True,
                default=datetime.datetime(
                    2023, 4, 23, 9, 48, 48, 563921, tzinfo=datetime.timezone.utc
                ),
            ),
        ),
    ]