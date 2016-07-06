# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0023_auto_20160531_1900'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(help_text='DateTime this model instance was created.', null=True, blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', default=oilserver.utils.time_now)),
                ('name', models.CharField(help_text='The type of product.', max_length=255, unique=True)),
                ('uuid', models.CharField(help_text='UUID of this type of product.', max_length=36, unique=True, default=oilserver.utils.generate_uuid)),
                ('toplevel', models.BooleanField(help_text='If this is a top-level config option to a pipeline.', default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='productundertest',
            name='producttype',
            field=models.ForeignKey(null=True, blank=True, default=None, to='oilserver.ProductType'),
            preserve_default=True,
        ),
    ]
