# Generated by Django 3.2.16 on 2023-04-20 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('zenodo_integration_app', '0003_remove_zenodoexperiment_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zenodoexperiment',
            name='depo_id',
            field=models.JSONField(default=list),
        ),
    ]
