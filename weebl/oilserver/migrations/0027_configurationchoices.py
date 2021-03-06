# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0026_auto_20160527_1405'),
    ]

    sql = """CREATE EXTENSION IF NOT EXISTS tablefunc;
    create view oilserver_configurationchoices as select row_number() over() as id, pipeline_id, openstackversion, ubuntuversion, blockstorage, compute, database, imagestorage, sdn
from crosstab(
        $$select distinct
                oilserver_pipeline.id as pipeline_id,
                oilserver_openstackversion.name as openstackversion,
                oilserver_ubuntuversion.name as ubuntuversion,
                oilserver_producttype.name as product_type,
                oilserver_productundertest.name as product_name
        from
                oilserver_openstackversion,
                oilserver_ubuntuversion,
                oilserver_versionconfiguration,
                oilserver_pipeline,
                oilserver_jujuservicedeployment,
                oilserver_productundertest,
                oilserver_producttype
        where
                oilserver_versionconfiguration.openstackversion_id = oilserver_openstackversion.id and
                oilserver_versionconfiguration.ubuntuversion_id = oilserver_ubuntuversion.id and
                oilserver_pipeline.versionconfiguration_id = oilserver_versionconfiguration.id and
                oilserver_jujuservicedeployment.pipeline_id = oilserver_pipeline.id and
                oilserver_jujuservicedeployment.productundertest_id = oilserver_productundertest.id
                and oilserver_productundertest.producttype_id = oilserver_producttype.id
                and oilserver_producttype.toplevel = True
        order by pipeline_id$$,
        'select distinct name from oilserver_producttype order by name;')
AS t(
        "pipeline_id" int,
        "openstackversion" varchar,
        "ubuntuversion" varchar,
        "blockstorage" varchar,
        "compute" varchar,
        "database" varchar,
        "imagestorage" varchar,
        "sdn" varchar)
GROUP BY openstackversion, ubuntuversion, blockstorage, compute, database, imagestorage, sdn, pipeline_id
ORDER BY pipeline_id ASC;"""

    operations = [
        migrations.RunSQL(sql),
        migrations.CreateModel(
            name='ConfigurationChoices',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('openstackversion', models.CharField(help_text='The openstackversion choice.', blank=True, null=True, max_length=255)),
                ('ubuntuversion', models.CharField(help_text='The ubuntuversion choice.', blank=True, null=True, max_length=255)),
                ('blockstorage', models.CharField(help_text='The blockstorage choice.', blank=True, null=True, max_length=255)),
                ('compute', models.CharField(help_text='The compute choice.', blank=True, null=True, max_length=255)),
                ('database', models.CharField(help_text='The database choice.', blank=True, null=True, max_length=255)),
                ('imagestorage', models.CharField(help_text='The imagestorage choice.', blank=True, null=True, max_length=255)),
                ('sdn', models.CharField(help_text='The sdn choice.', blank=True, null=True, max_length=255)),
            ],
            options={
                'managed': False,
            },
            bases=(models.Model,),
        ),
    ]
