# Generated by Django 4.1 on 2022-09-09 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0011_remove_transaction_booking"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="transaction",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="booking",
                to="organizations.transaction",
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="rent_amount",
            field=models.FloatField(null=True),
        ),
    ]
