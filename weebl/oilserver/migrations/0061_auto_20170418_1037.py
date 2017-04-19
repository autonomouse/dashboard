# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0060_auto_20170411_1313'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='releasedate',
            unique_together=set([]),
        ),
    ]
