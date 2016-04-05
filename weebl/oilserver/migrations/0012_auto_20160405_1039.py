# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0011_auto_20160404_2139'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='number',
            field=models.IntegerField(default=0, help_text='Number of this unit (unit is: service_name/unit_number).'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='unit',
            name='uuid',
            field=models.CharField(unique=True, default=oilserver.utils.generate_uuid, help_text='UUID of this unit.', max_length=36),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='unit',
            unique_together=set([('number', 'jujuservicedeployment')]),
        ),
        migrations.RemoveField(
            model_name='unit',
            name='name',
        ),
    ]
