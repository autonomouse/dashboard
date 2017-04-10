# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0057_solutiontag_show'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobtype',
            name='plot',
            field=models.BooleanField(help_text='Show on plots (e.g. success rate and trends graphs).', default=False),
        ),
    ]
