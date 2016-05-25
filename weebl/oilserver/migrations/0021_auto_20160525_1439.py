# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0020_weeblsetting'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcaseinstancestatus',
            name='created_at',
            field=models.DateTimeField(null=True, default=None, help_text='DateTime this model instance was created.', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testcaseinstancestatus',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
            preserve_default=True,
        ),
    ]
