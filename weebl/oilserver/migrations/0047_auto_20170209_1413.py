# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, transaction, models

def set_success_to_none(apps, schema_editor):
    """So that we know what historical data is correct, set the success value
    to None for starting"""
    from oilserver.models import JujuServiceDeployment
    with transaction.atomic():
        for deployment in JujuServiceDeployment.objects.all():
            deployment.success = None
            deployment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0046_reportsection_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jujuservicedeployment',
            name='success',
            field=models.NullBooleanField(help_text='Whether this juju service deployed successfully.', default=None),
        ),
        migrations.RunPython(set_success_to_none),
    ]
