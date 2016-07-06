# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0025_auto_20160526_2312'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pipeline',
            name='blockstorage',
        ),
        migrations.DeleteModel(
            name='BlockStorage',
        ),
        migrations.RemoveField(
            model_name='pipeline',
            name='compute',
        ),
        migrations.DeleteModel(
            name='Compute',
        ),
        migrations.RemoveField(
            model_name='pipeline',
            name='database',
        ),
        migrations.DeleteModel(
            name='Database',
        ),
        migrations.RemoveField(
            model_name='pipeline',
            name='imagestorage',
        ),
        migrations.DeleteModel(
            name='ImageStorage',
        ),
        migrations.RemoveField(
            model_name='pipeline',
            name='sdn',
        ),
        migrations.DeleteModel(
            name='SDN',
        ),
    ]
