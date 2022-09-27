# Generated by Django 3.2.15 on 2022-09-05 10:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0002_property'),
    ]

    operations = [
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_at', models.DateTimeField(blank=True, null=True)),
                ('end_at', models.DateTimeField(blank=True, null=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('payment_mode', models.CharField(choices=[('NULL', 'Null'), ('CASH', 'CASH'), ('ONLINE', 'ONLINE')], default='NULL', max_length=150)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booking', to='organizations.property')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booking', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
