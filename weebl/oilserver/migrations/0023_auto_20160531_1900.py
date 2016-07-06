# -*- coding: utf-8 -*-
# pylint: disable=C0103

from __future__ import unicode_literals

from django.db import models, migrations


def jujuservicedeployments_build_to_pipeline(apps, schema_editor):
    JujuServiceDeployment = apps.get_model('oilserver',
                                           'JujuServiceDeployment')
    for jujuservicedeployment in JujuServiceDeployment.objects.all():
        jujuservicedeployment.pipeline = jujuservicedeployment.build.pipeline
        jujuservicedeployment.build = None
        jujuservicedeployment.save()


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0022_auto_20160524_1703'),
    ]

    operations = [
        migrations.AddField(
            model_name='jujuservicedeployment',
            name='pipeline',
            field=models.ForeignKey(null=True, to='oilserver.Pipeline'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='jujuservicedeployment',
            unique_together=set([('pipeline', 'charm', 'jujuservice')]),
        ),
        migrations.RunPython(
            jujuservicedeployments_build_to_pipeline
        ),
        migrations.RemoveField(
            model_name='jujuservicedeployment',
            name='build',
        ),
    ]
