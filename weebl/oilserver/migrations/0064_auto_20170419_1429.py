# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0063_include_producttypeversion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='releasedate',
            name='releasetype',
        ),
        migrations.RemoveField(
            model_name='productundertest',
            name='producttype',
        ),
        migrations.AlterField(
            model_name='release',
            name='actualrelease',
            field=models.BooleanField(help_text='This was the actual release of the product.'),
        ),
        migrations.AlterField(
            model_name='release',
            name='releasedate',
            field=models.DateField(help_text='Date the pipeline was completed.', default=oilserver.utils.time_now),
        ),
        migrations.AlterUniqueTogether(
            name='release',
            unique_together=set([('producttypeversion', 'releasetype', 'actualrelease', 'releasedate')]),
        ),
        migrations.AlterUniqueTogether(
            name='releasetype',
            unique_together=set([]),
        ),
        migrations.DeleteModel(
            name='ReleaseDate',
        ),
        migrations.RemoveField(
            model_name='release',
            name='producttype',
        ),
        migrations.RemoveField(
            model_name='release',
            name='trackedversion',
        ),
        migrations.RemoveField(
            model_name='releasetype',
            name='release',
        ),
    ]
