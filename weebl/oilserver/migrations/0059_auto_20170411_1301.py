# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0058_auto_20170410_0957'),
    ]

    operations = [
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(default=None, blank=True, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('trackedversion', models.TextField(default='1.0', help_text='Version of this release.')),
                ('tracking', models.TextField(default=None, blank=True, help_text='URL to where this release is tracked.', null=True)),
                ('show', models.BooleanField(default=True, help_text='Show in release tracker.')),
                ('uuid', models.CharField(unique=True, default=oilserver.utils.generate_uuid, max_length=36, help_text='UUID of this type of product.')),
                ('producttype', models.ForeignKey(to='oilserver.ProductType', blank=True, null=True, default=None)),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseDate',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(default=None, blank=True, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('date', models.DateField(default=None, blank=True, help_text='Date the pipeline was completed.', null=True)),
                ('uuid', models.CharField(unique=True, default=oilserver.utils.generate_uuid, max_length=36, help_text='UUID of this type of product.')),
                ('actualrelease', models.BooleanField(default=False, help_text='This was the actual release of the product.')),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseType',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(default=None, blank=True, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('name', models.CharField(unique=True, default='beta', max_length=255, help_text='The type of release.')),
                ('release', models.ForeignKey(to='oilserver.Release', blank=True, null=True, default=None, related_name='releasetypes')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='releasedate',
            name='releasetype',
            field=models.ForeignKey(to='oilserver.ReleaseType', blank=True, null=True, default=None, related_name='releasedates'),
        ),
        migrations.AlterUniqueTogether(
            name='releasedate',
            unique_together=set([('releasetype', 'actualrelease')]),
        ),
        migrations.AlterUniqueTogether(
            name='release',
            unique_together=set([('producttype', 'trackedversion')]),
        ),
    ]
