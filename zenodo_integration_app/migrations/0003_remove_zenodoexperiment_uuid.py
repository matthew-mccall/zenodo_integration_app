# Generated by Django 3.2.16 on 2023-03-30 17:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zenodo_integration_app', '0002_zenodoexperiment_depo_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zenodoexperiment',
            name='uuid',
        ),
    ]
