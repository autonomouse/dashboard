# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0035_auto_20161020_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='internalcontact',
            name='staffdirectoryurl',
            field=models.URLField(help_text='URL linking to Canonical staff directory.', default=None, blank=True, null=True),
        ),
    ]
