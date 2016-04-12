# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0013_auto_20160408_1258'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='testcase',
            unique_together=set([('name', 'testcaseclass')]),
        ),
    ]
