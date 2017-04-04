# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0054_auto_20170310_1810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='environment',
            name='data_archive_url',
            field=models.URLField(blank=True, default='', help_text='A base URL to the data archive used.'),
        ),
        migrations.AlterField(
            model_name='jenkins',
            name='external_access_url',
            field=models.URLField(null=True, blank=True, help_text='A URL for external access to this server.'),
        ),
        migrations.AlterField(
            model_name='jenkins',
            name='internal_access_url',
            field=models.URLField(default=None, help_text='A URL used internally (e.g. behind a firewall) for access         to this server.', unique=True),
        ),
    ]
