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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(null=True, default=None, help_text='DateTime this model instance was created.', blank=True)),
                ('updated_at', models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('cdo_checksum', models.CharField(max_length=255, unique=True, help_text='MD5 checksum used by CDO QA to identify this solution.')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SolutionTag',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(null=True, default=None, help_text='DateTime this model instance was created.', blank=True)),
                ('updated_at', models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('name', models.CharField(max_length=255, unique=True, help_text='The current name of the solution.')),
                ('colour', models.CharField(max_length=6, default='56334b', help_text="HTML colour code (excluding the '#' prefix).")),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='solution',
            name='solutiontag',
            field=models.OneToOneField(to='oilserver.SolutionTag', default=None, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pipeline',
            name='solution',
            field=models.ForeignKey(to='oilserver.Solution', default=None, blank=True, null=True),
        ),
    ]
