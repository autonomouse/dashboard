# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0012_auto_20160405_1039'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='build',
            name='artifact_location',
        ),
        migrations.AddField(
            model_name='environment',
            name='data_archive_url',
            field=models.URLField(blank=True, help_text='A base URL to the data archive used.', default=None, null=True),
            preserve_default=True,
        ),
    ]
