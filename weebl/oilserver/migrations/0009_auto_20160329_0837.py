# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0008_transform_buildstatus_to_testcaseinstancestatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='testcase',
            name='uuid',
            field=models.CharField(max_length=36, null=True, help_text='UUID of this testcase.', default=oilserver.utils.generate_uuid),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testcaseclass',
            name='uuid',
            field=models.CharField(max_length=36, null=True, help_text='UUID of this testcaseclass.', default=oilserver.utils.generate_uuid),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testframework',
            name='uuid',
            field=models.CharField(max_length=36, null=True, help_text='UUID of this test framework and version.', default=oilserver.utils.generate_uuid),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcase',
            name='name',
            field=models.CharField(max_length=255, help_text='Name of this individual test case.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcaseclass',
            name='name',
            field=models.CharField(max_length=255, help_text='Name of this individual test case.'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testframework',
            name='name',
            field=models.CharField(max_length=255, help_text='Name of the testing framework.'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='testcaseclass',
            unique_together=set([('name', 'testframework')]),
        ),
        migrations.AlterUniqueTogether(
            name='testframework',
            unique_together=set([('name', 'version')]),
        ),
    ]
