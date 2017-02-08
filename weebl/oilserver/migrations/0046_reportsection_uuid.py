# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0045_testreportview'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportsection',
            name='uuid',
            field=models.CharField(help_text='UUID of the report section.', max_length=36, unique=True, default=oilserver.utils.generate_uuid),
        ),
    ]
