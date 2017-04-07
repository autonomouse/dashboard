# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0056_testcaseclassname_switch'),
    ]

    operations = [
        migrations.AddField(
            model_name='solutiontag',
            name='show',
            field=models.BooleanField(help_text='Show on front page.', default=True),
        ),
    ]
