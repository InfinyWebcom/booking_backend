# Generated by Django 3.2.15 on 2022-09-15 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0020_booking_booking_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='pending_amount',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='booking',
            name='booking_amount',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
