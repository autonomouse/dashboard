# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0033_update_unknown_testcasestatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jenkins',
            name='external_access_url',
            field=models.URLField(help_text='A URL for external access to this server.'),
        ),
    ]
