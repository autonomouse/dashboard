# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0002_auto_20151209_1650'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productundertest',
            name='machine',
        ),
        migrations.AddField(
            model_name='machine',
            name='hostname',
            field=models.CharField(null=True, default=None, help_text='Host name or IP address ofthis machine.', max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='machineconfiguration',
            name='productundertest',
            field=models.ManyToManyField(to='oilserver.ProductUnderTest', default=None, null=True, blank=True),
            preserve_default=True,
        ),
    ]
