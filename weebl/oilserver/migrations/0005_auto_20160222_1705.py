# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0004_auto_20160115_1741'),
    ]

    operations = [
        migrations.CreateModel(
            name='JujuService',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('created_at', models.DateTimeField(null=True, default=None, blank=True, help_text='DateTime this model instance was created.')),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('uuid', models.CharField(default=oilserver.utils.generate_uuid, unique=True, max_length=36, help_text='UUID of this Juju service.')),
                ('name', models.CharField(default='unknown', unique=True, max_length=255, help_text='The name of the Juju service.')),
                ('productundertest', models.ForeignKey(to='oilserver.ProductUnderTest', default=None, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JujuServiceDeployment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('created_at', models.DateTimeField(null=True, default=None, blank=True, help_text='DateTime this model instance was created.')),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('uuid', models.CharField(default=oilserver.utils.generate_uuid, unique=True, max_length=36, help_text='UUID of this juju service deployment.')),
                ('jujuservice', models.ForeignKey(to='oilserver.JujuService', default=None, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('created_at', models.DateTimeField(null=True, default=None, blank=True, help_text='DateTime this model instance was created.')),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('name', models.CharField(default='unknown', unique=True, max_length=255, help_text='The name of the unit.')),
                ('jujuservicedeployment', models.ForeignKey(to='oilserver.JujuServiceDeployment', default=None, null=True, blank=True)),
                ('machineconfiguration', models.ForeignKey(to='oilserver.MachineConfiguration', default=None, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='weeblsetting',
            name='site',
        ),
        migrations.DeleteModel(
            name='WeeblSetting',
        ),
    ]
