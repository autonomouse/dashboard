# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0053_testreportviewfix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solution',
            name='solutiontag',
            field=models.ForeignKey(null=True, blank=True, default=None, to='oilserver.SolutionTag'),
        ),
    ]
