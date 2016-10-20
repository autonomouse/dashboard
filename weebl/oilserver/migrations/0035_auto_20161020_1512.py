# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0034_auto_20160922_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ubuntuversion',
            name='number',
            field=models.CharField(default='', max_length=10, help_text='The numerical version of the Ubuntu system'),
        ),
        migrations.AlterUniqueTogether(
            name='ubuntuversion',
            unique_together=set([('name', 'number')]),
        ),
    ]
