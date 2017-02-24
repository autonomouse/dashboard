# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0050_amend_jobtype_descriptions_and_colours'),
    ]

    operations = [
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', blank=True, null=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', default=oilserver.utils.time_now)),
                ('cdo_checksum', models.CharField(unique=True, max_length=255, help_text='MD5 checksum used by CDO QA to identify this solution.')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SolutionTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', blank=True, null=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', default=oilserver.utils.time_now)),
                ('name', models.CharField(unique=True, max_length=255, help_text='The current name of the solution.')),
                ('colour', models.CharField(max_length=6, help_text="HTML colour code (excluding the '#' prefix).", default='56334b')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='solution',
            name='solutiontag',
            field=models.OneToOneField(blank=True, null=True, default=None, to='oilserver.SolutionTag'),
        ),
        migrations.AddField(
            model_name='pipeline',
            name='solution',
            field=models.ForeignKey(blank=True, null=True, default=None, to='oilserver.Solution'),
        ),
    ]
