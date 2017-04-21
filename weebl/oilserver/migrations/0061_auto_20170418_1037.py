# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0060_auto_20170411_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='releasetype',
            name='release',
            field=models.OneToOneField(null=True, related_name='releasetypes', to='oilserver.Release', default=None, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='releasedate',
            unique_together=set([]),
        ),
    ]