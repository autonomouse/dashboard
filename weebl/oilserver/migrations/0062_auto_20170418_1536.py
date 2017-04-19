# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0061_auto_20170418_1037'),
    ]

    operations = [
        migrations.AlterField(
            model_name='releasetype',
            name='name',
            field=models.CharField(max_length=255, help_text='The type of release.', default='final'),
        ),
        migrations.AlterField(
            model_name='releasetype',
            name='release',
            field=models.ForeignKey(blank=True, to='oilserver.Release', null=True, related_name='releasetypes', default=None),
        ),
        migrations.AlterUniqueTogether(
            name='releasetype',
            unique_together=set([('release', 'name')]),
        ),
    ]
