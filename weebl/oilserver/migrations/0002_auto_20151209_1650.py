# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from oilserver import utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InternalContact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, help_text='DateTime this model instance was last updated.', default=utils.time_now)),
                ('name', models.CharField(unique=True, help_text='The name and/or number of the product type.', max_length=255)),
                ('staffdirectoryurl', models.URLField(blank=True, help_text='URL linking to Canonical staff directory.', default=None)),
                ('uuid', models.CharField(unique=True, help_text='UUID of this contact.', max_length=36, default=utils.generate_uuid)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, help_text='DateTime this model instance was last updated.', default=utils.time_now)),
                ('uuid', models.CharField(unique=True, help_text='UUID of this machine.', max_length=36, default=utils.generate_uuid)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MachineConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, help_text='DateTime this model instance was last updated.', default=utils.time_now)),
                ('uuid', models.CharField(unique=True, help_text='UUID of this machine.', max_length=36, default=utils.generate_uuid)),
                ('machine', models.ForeignKey(default=None, blank=True, to='oilserver.Machine', null=True)),
                ('pipeline', models.ForeignKey(default=None, blank=True, to='oilserver.Pipeline', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductUnderTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, help_text='DateTime this model instance was last updated.', default=utils.time_now)),
                ('name', models.CharField(unique=True, help_text='The name of the product.', max_length=255)),
                ('uuid', models.CharField(unique=True, help_text='UUID of this product.', max_length=36, default=utils.generate_uuid)),
                ('internalcontact', models.ForeignKey(default=None, blank=True, to='oilserver.InternalContact', null=True)),
                ('machine', models.ManyToManyField(blank=True, default=None, to='oilserver.Machine', null=True)),
                ('project', models.ForeignKey(default=None, blank=True, to='oilserver.Project', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(blank=True, default=None, help_text='DateTime this model instance was created.', null=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True, help_text='DateTime this model instance was last updated.', default=utils.time_now)),
                ('name', models.CharField(unique=True, help_text='The name and/or number of the product type.', max_length=255)),
                ('uuid', models.CharField(unique=True, help_text='UUID of this vendor.', max_length=36, default=utils.generate_uuid)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='productundertest',
            name='vendor',
            field=models.ForeignKey(default=None, blank=True, to='oilserver.Vendor', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='uuid',
            field=models.CharField(unique=True, help_text='UUID of this project.', max_length=36, default=utils.generate_uuid),
            preserve_default=True,
        ),
    ]
