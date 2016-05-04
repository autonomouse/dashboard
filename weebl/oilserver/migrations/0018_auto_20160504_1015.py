# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0017_remove_duplicate_testcaseinstances'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcaseinstance',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True, default=None, help_text='DateTime this model instance was created.'),
        ),
        migrations.AddField(
            model_name='testcaseinstance',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='testcaseinstance',
            name='build',
            field=models.ForeignKey(to='oilserver.Build', default=None),
        ),
        migrations.AlterField(
            model_name='testcaseinstance',
            name='testcase',
            field=models.ForeignKey(to='oilserver.TestCase', default=None),
        ),
        migrations.AlterUniqueTogether(
            name='build',
            unique_together=set([('pipeline', 'jobtype')]),
        ),
        migrations.AlterUniqueTogether(
            name='testcaseinstance',
            unique_together=set([('testcase', 'build')]),
        ),
    ]
