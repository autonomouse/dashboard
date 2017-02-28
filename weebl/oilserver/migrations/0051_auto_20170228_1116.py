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
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(null=True, default=None, help_text='DateTime this model instance was created.', blank=True)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', default=oilserver.utils.time_now)),
                ('cdo_checksum', models.CharField(help_text='MD5 checksum used by CDO QA to identify this solution.', max_length=255, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SolutionTag',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(null=True, default=None, help_text='DateTime this model instance was created.', blank=True)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', default=oilserver.utils.time_now)),
                ('name', models.CharField(help_text='The current name of the solution.', max_length=255, unique=True)),
                ('colour', models.CharField(help_text="HTML colour code (excluding the '#' prefix).", max_length=6, default='56334b')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='solution',
            name='solutiontag',
            field=models.OneToOneField(null=True, blank=True, to='oilserver.SolutionTag', default=None),
        ),
        migrations.AddField(
            model_name='pipeline',
            name='solution',
            field=models.ForeignKey(null=True, blank=True, to='oilserver.Solution', default=None),
        ),
    ]
