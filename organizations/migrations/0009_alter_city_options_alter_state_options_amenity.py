# Generated by Django 4.1 on 2022-09-09 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0008_property_owner"),
    ]

    operations = [
        migrations.AlterModelOptions(name="city", options={"ordering": ["name"]},),
        migrations.AlterModelOptions(name="state", options={"ordering": ["name"]},),
        migrations.CreateModel(
            name="Amenity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(blank=True, max_length=256, null=True)),
                (
                    "property",
                    models.ManyToManyField(
                        related_name="amenities", to="organizations.property"
                    ),
                ),
            ],
        ),
    ]
