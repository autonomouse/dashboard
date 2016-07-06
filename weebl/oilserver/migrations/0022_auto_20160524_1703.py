# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oilserver.utils
from oilserver.utils import get_or_create_new_model


def pipeline_versionconfiguration_to_separate_table(apps, schema_editor):
    Pipeline = apps.get_model('oilserver', 'Pipeline')
    for pipeline in Pipeline.objects.all():
        version_dict = {
            'ubuntuversion': pipeline.ubuntuversion,
            'openstackversion': pipeline.openstackversion
        }
        versionconfiguration = get_or_create_new_model(
            apps.get_model('oilserver', 'VersionConfiguration'),
            tuple(sorted(version_dict.keys())),
            version_dict)
        pipeline.versionconfiguration = versionconfiguration
        pipeline.save()


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0021_auto_20160524_1631'),
    ]

    operations = [
        migrations.CreateModel(
            name='VersionConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(default=None, null=True, blank=True, help_text='DateTime this model instance was created.')),
                ('updated_at', models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('uuid', models.CharField(default=oilserver.utils.generate_uuid, unique=True, max_length=36, help_text='UUID of this VersionConfiguration.')),
                ('openstackversion', models.ForeignKey(null=True, default=None, blank=True, to='oilserver.OpenstackVersion')),
                ('ubuntuversion', models.ForeignKey(null=True, default=None, blank=True, to='oilserver.UbuntuVersion')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='versionconfiguration',
            unique_together=set([('ubuntuversion', 'openstackversion')]),
        ),
        migrations.AddField(
            model_name='pipeline',
            name='versionconfiguration',
            field=models.ForeignKey(null=True, default=None, blank=True, to='oilserver.VersionConfiguration'),
            preserve_default=True,
        ),
        migrations.RunPython(
            pipeline_versionconfiguration_to_separate_table
        ),
        migrations.RemoveField(
            model_name='pipeline',
            name='openstackversion',
        ),
        migrations.RemoveField(
            model_name='pipeline',
            name='ubuntuversion',
        ),
    ]
