# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0030_add_skipped_testcaseinstancestatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knownbugregex',
            name='targetfileglobs',
            field=models.ManyToManyField(related_name='knownbugregexes', to='oilserver.TargetFileGlob'),
        ),
    ]
