# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0005_auto_20160222_1705'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='build',
            unique_together=set([('build_id', 'pipeline', 'jobtype')]),
        ),
    ]
