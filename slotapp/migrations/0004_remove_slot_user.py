# Generated by Django 3.2.15 on 2022-09-12 09:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('slotapp', '0003_alter_slot_property_alter_slot_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='slot',
            name='user',
        ),
    ]