# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


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
    ]
