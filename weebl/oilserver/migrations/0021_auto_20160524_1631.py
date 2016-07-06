# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0021_auto_20160525_1439'),
    ]

    operations = [
        migrations.CreateModel(
            name='Charm',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('created_at', models.DateTimeField(default=None, null=True, blank=True, help_text='DateTime this model instance was created.')),
                ('updated_at', models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('uuid', models.CharField(max_length=36, default=oilserver.utils.generate_uuid, help_text='UUID of this Juju charm.', unique=True)),
                ('name', models.CharField(max_length=255, default='unknown', help_text='The name of the Juju charm.')),
                ('charm_source_url', models.URLField(help_text='The source of this charm.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RenameField(
            model_name='bugoccurrence',
            old_name='regex',
            new_name='knownbugregex',
        ),
        migrations.RemoveField(
            model_name='jujuservice',
            name='productundertest',
        ),
        migrations.RemoveField(
            model_name='machineconfiguration',
            name='pipeline',
        ),
        migrations.AddField(
            model_name='jujuservicedeployment',
            name='build',
            field=models.ForeignKey(null=True, to='oilserver.Build'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jujuservicedeployment',
            name='charm',
            field=models.ForeignKey(null=True, to='oilserver.Charm'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='jujuservicedeployment',
            name='productundertest',
            field=models.ForeignKey(null=True, to='oilserver.ProductUnderTest'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcase',
            name='testcaseclass',
            field=models.ForeignKey(null=True, to='oilserver.TestCaseClass'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='testcaseclass',
            name='testframework',
            field=models.ForeignKey(null=True, to='oilserver.TestFramework'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='unit',
            name='jujuservicedeployment',
            field=models.ForeignKey(null=True, to='oilserver.JujuServiceDeployment'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='bugoccurrence',
            unique_together=set([('testcaseinstance', 'knownbugregex')]),
        ),
        migrations.AlterUniqueTogether(
            name='jujuservicedeployment',
            unique_together=set([('build', 'charm', 'jujuservice')]),
        ),
        migrations.AlterUniqueTogether(
            name='productundertest',
            unique_together=set([('name', 'vendor')]),
        ),
        migrations.AlterUniqueTogether(
            name='reportinstance',
            unique_together=set([('report', 'report_period')]),
        ),
    ]
