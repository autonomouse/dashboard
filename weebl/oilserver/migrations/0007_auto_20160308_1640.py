# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0006_auto_20160301_2240'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', blank=True, default=None, null=True)),
                ('updated_at', models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.', auto_now_add=True)),
                ('uuid', models.CharField(help_text='UUID of this report.', default=oilserver.utils.generate_uuid, unique=True, max_length=36)),
                ('name', models.CharField(help_text='Pretty name for this report.', max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReportInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', blank=True, default=None, null=True)),
                ('updated_at', models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.', auto_now_add=True)),
                ('uuid', models.CharField(help_text='UUID of this report instance.', default=oilserver.utils.generate_uuid, unique=True, max_length=36)),
                ('specific_summary', models.TextField(help_text='Summary text for specific report.', blank=True, default=None, null=True)),
                ('report', models.ForeignKey(to='oilserver.Report')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReportPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', blank=True, default=None, null=True)),
                ('updated_at', models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.', auto_now_add=True)),
                ('uuid', models.CharField(help_text='UUID of this time range.', default=oilserver.utils.generate_uuid, unique=True, max_length=36)),
                ('name', models.CharField(help_text='Pretty name for time range.', max_length=255, unique=True)),
                ('start_date', models.DateTimeField(help_text='Start DateTime reports of this period will cover.', default=None)),
                ('end_date', models.DateTimeField(help_text='End DateTime reports of this period will cover.', default=None)),
                ('overall_summary', models.TextField(help_text='Summary text for time period.', blank=True, default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='reportinstance',
            name='report_period',
            field=models.ForeignKey(to='oilserver.ReportPeriod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='productundertest',
            name='report',
            field=models.ManyToManyField(blank=True, default=None, to='oilserver.Report', null=True),
            preserve_default=True,
        ),
    ]
