# Generated by Django 5.0.1 on 2024-02-13 15:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0003_machineprice_machinemaintenance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='machinemaintenance',
            name='maintenance_schedule',
        ),
    ]
