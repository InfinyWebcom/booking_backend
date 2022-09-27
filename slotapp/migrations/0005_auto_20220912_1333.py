# Generated by Django 3.2.15 on 2022-09-12 13:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0017_remove_booking_slot'),
        ('slotapp', '0004_remove_slot_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='slot',
            name='booking',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='slot_booked', to='organizations.booking'),
        ),
        migrations.AlterField(
            model_name='slot',
            name='property',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='slot_property', to='organizations.property'),
        ),
    ]
