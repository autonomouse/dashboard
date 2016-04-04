# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0010_auto_20160404_2138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testcase',
            name='uuid',
            field=models.CharField(max_length=36, unique=True, help_text='UUID of this testcase.', default=oilserver.utils.generate_uuid),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcaseclass',
            name='uuid',
            field=models.CharField(max_length=36, unique=True, help_text='UUID of this testcaseclass.', default=oilserver.utils.generate_uuid),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testframework',
            name='uuid',
            field=models.CharField(max_length=36, unique=True, help_text='UUID of this test framework and version.', default=oilserver.utils.generate_uuid),
            preserve_default=True,
        ),
    ]
