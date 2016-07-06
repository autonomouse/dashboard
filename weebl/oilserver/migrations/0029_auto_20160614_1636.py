# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0028_auto_20160609_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bugoccurrence',
            name='testcaseinstance',
            field=models.ForeignKey(blank=True, to='oilserver.TestCaseInstance', default=None, related_name='bugoccurrences', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bugtrackerbug',
            name='project',
            field=models.ForeignKey(blank=True, to='oilserver.Project', default=None, related_name='bugtrackerbugs', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='build',
            name='jobtype',
            field=models.ForeignKey(to='oilserver.JobType', related_name='builds'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='buildexecutor',
            name='jenkins',
            field=models.ForeignKey(to='oilserver.Jenkins', related_name='buildexecutors'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jenkins',
            name='servicestatus',
            field=models.ForeignKey(to='oilserver.ServiceStatus', related_name='jenkinses'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jujuservicedeployment',
            name='charm',
            field=models.ForeignKey(to='oilserver.Charm', null=True, related_name='jujuservicedeployments'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pipeline',
            name='buildexecutor',
            field=models.ForeignKey(to='oilserver.BuildExecutor', related_name='pipelines'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productundertest',
            name='project',
            field=models.ForeignKey(blank=True, to='oilserver.Project', default=None, related_name='productundertests', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reportinstance',
            name='report',
            field=models.ForeignKey(to='oilserver.Report', related_name='reportinstances'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='reportinstance',
            name='reportperiod',
            field=models.ForeignKey(to='oilserver.ReportPeriod', related_name='reportinstances'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='targetfileglob',
            name='jobtypes',
            field=models.ManyToManyField(blank=True, to='oilserver.JobType', related_name='targetfileglobs', default=None, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcase',
            name='testcaseclass',
            field=models.ForeignKey(to='oilserver.TestCaseClass', null=True, related_name='testcases'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcaseclass',
            name='testframework',
            field=models.ForeignKey(to='oilserver.TestFramework', null=True, related_name='testcaseclasses'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcaseinstance',
            name='testcase',
            field=models.ForeignKey(to='oilserver.TestCase', default=None, related_name='testcaseinstances'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcaseinstance',
            name='testcaseinstancestatus',
            field=models.ForeignKey(blank=True, to='oilserver.TestCaseInstanceStatus', default=None, related_name='testcaseinstances', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='versionconfiguration',
            name='openstackversion',
            field=models.ForeignKey(blank=True, to='oilserver.OpenstackVersion', default=None, related_name='versionconfigurations', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='versionconfiguration',
            name='ubuntuversion',
            field=models.ForeignKey(blank=True, to='oilserver.UbuntuVersion', default=None, related_name='versionconfigurations', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weeblsetting',
            name='default_environment',
            field=models.OneToOneField(blank=True, to='oilserver.Environment', default=None, help_text='The default environment to display. If none, displays all.', null=True),
            preserve_default=True,
        ),
    ]
