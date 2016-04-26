# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0014_auto_20160412_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bug',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='bugoccurrence',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='bugtrackerbug',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='build',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='buildexecutor',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='environment',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='internalcontact',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='jenkins',
            name='servicestatus_updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime the service status was last updated.'),
        ),
        migrations.AlterField(
            model_name='jenkins',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='jujuservice',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='jujuservicedeployment',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='knownbugregex',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='machine',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='machineconfiguration',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='pipeline',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='productundertest',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='project',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='report',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='reportinstance',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='reportperiod',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='targetfileglob',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='testcase',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='testcaseclass',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='testframework',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='unit',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='updated_at',
            field=models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.'),
        ),
    ]
