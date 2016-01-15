# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0003_auto_20151223_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='machine',
            name='hostname',
            field=models.CharField(default=None, blank=True, null=True, unique=True, help_text='Host name or IP address of this machine.', max_length=255),
            preserve_default=True,
        ),
    ]

