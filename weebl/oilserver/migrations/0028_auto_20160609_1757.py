# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0027_configurationchoices'),
    ]

    operations = [
        migrations.RenameField(
            model_name='machineconfiguration',
            old_name='productundertest',
            new_name='productundertests',
        ),
        migrations.RenameField(
            model_name='productundertest',
            old_name='report',
            new_name='reports',
        ),
        migrations.RenameField(
            model_name='reportinstance',
            old_name='report_period',
            new_name='reportperiod',
        ),
        migrations.AlterUniqueTogether(
            name='reportinstance',
            unique_together=set([('report', 'reportperiod')]),
        ),
        migrations.AlterField(
            model_name='machineconfiguration',
            name='productundertests',
            field=models.ManyToManyField(default=None, to='oilserver.ProductUnderTest', blank=True, related_name='machineconfigurations', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productundertest',
            name='reports',
            field=models.ManyToManyField(default=None, to='oilserver.Report', blank=True, related_name='productundertests', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='bugoccurrence',
            name='knownbugregex',
            field=models.ForeignKey(to='oilserver.KnownBugRegex', related_name='bugoccurrences'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jujuservicedeployment',
            name='jujuservice',
            field=models.ForeignKey(default=None, to='oilserver.JujuService', null=True, blank=True, related_name='jujuservicedeployments'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jujuservicedeployment',
            name='productundertest',
            field=models.ForeignKey(to='oilserver.ProductUnderTest', null=True, related_name='jujuservicedeployments'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='knownbugregex',
            name='bug',
            field=models.ForeignKey(default=None, to='oilserver.Bug', null=True, blank=True, related_name='knownbugregexes'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='machineconfiguration',
            name='machine',
            field=models.ForeignKey(default=None, to='oilserver.Machine', null=True, blank=True, related_name='machineconfigurations'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pipeline',
            name='versionconfiguration',
            field=models.ForeignKey(default=None, to='oilserver.VersionConfiguration', null=True, blank=True, related_name='pipelines'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productundertest',
            name='producttype',
            field=models.ForeignKey(default=None, to='oilserver.ProductType', null=True, blank=True, related_name='productundertests'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productundertest',
            name='vendor',
            field=models.ForeignKey(default=None, to='oilserver.Vendor', null=True, blank=True, related_name='productundertests'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcaseinstance',
            name='build',
            field=models.ForeignKey(default=None, to='oilserver.Build', related_name='testcaseinstances'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unit',
            name='jujuservicedeployment',
            field=models.ForeignKey(to='oilserver.JujuServiceDeployment', null=True, related_name='units'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unit',
            name='machineconfiguration',
            field=models.ForeignKey(default=None, to='oilserver.MachineConfiguration', null=True, blank=True, related_name='units'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='jujuservicedeployment',
            name='pipeline',
            field=models.ForeignKey(null=True, to='oilserver.Pipeline', related_name='jujuservicedeployments'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='build',
            name='pipeline',
            field=models.ForeignKey(to='oilserver.Pipeline', related_name='builds'),
            preserve_default=True,
        ),
    ]
