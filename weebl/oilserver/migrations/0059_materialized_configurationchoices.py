# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


materialized_view = """CREATE EXTENSION IF NOT EXISTS tablefunc;
    DROP VIEW oilserver_configurationchoices;
    CREATE MATERIALIZED VIEW oilserver_configurationchoices AS SELECT row_number() over() AS id, pipeline_id, openstackversion, ubuntuversion, blockstorage, compute, database, imagestorage, sdn
FROM crosstab(
        $$SELECT DISTINCT
                oilserver_pipeline.id as pipeline_id,
                oilserver_openstackversion.name as openstackversion,
                oilserver_ubuntuversion.name as ubuntuversion,
                oilserver_producttype.name as product_type,
                oilserver_productundertest.name as product_name
        FROM
                oilserver_openstackversion,
                oilserver_ubuntuversion,
                oilserver_versionconfiguration,
                oilserver_pipeline,
                oilserver_jujuservicedeployment,
                oilserver_productundertest,
                oilserver_producttype
        WHERE
                oilserver_versionconfiguration.openstackversion_id = oilserver_openstackversion.id and
                oilserver_versionconfiguration.ubuntuversion_id = oilserver_ubuntuversion.id and
                oilserver_pipeline.versionconfiguration_id = oilserver_versionconfiguration.id and
                oilserver_jujuservicedeployment.pipeline_id = oilserver_pipeline.id and
                oilserver_jujuservicedeployment.productundertest_id = oilserver_productundertest.id
                and oilserver_productundertest.producttype_id = oilserver_producttype.id
                and oilserver_producttype.toplevel = True
        ORDER BY pipeline_id$$,
        'SELECT DISTINCT name FROM oilserver_producttype WHERE toplevel = True ORDER BY name;')
AS t(
        "pipeline_id" int,
        "openstackversion" varchar,
        "ubuntuversion" varchar,
        "blockstorage" varchar,
        "compute" varchar,
        "database" varchar,
        "imagestorage" varchar,
        "sdn" varchar)
GROUP BY openstackversion, ubuntuversion, blockstorage, compute, database, imagestorage, sdn, pipeline_id;
CREATE INDEX ON oilserver_configurationchoices ( pipeline_id );
CREATE OR REPLACE FUNCTION refresh_configurationchoices_materialized_view()
RETURNS trigger LANGUAGE plpgsql
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW oilserver_configurationchoices;
    RETURN NULL;
END $$;

CREATE TRIGGER refresh_configurationchoices
AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE
ON oilserver_pipeline FOR EACH STATEMENT
EXECUTE PROCEDURE refresh_configurationchoices_materialized_view();

CREATE TRIGGER refresh_configurationchoices
AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE
ON oilserver_jujuservicedeployment FOR EACH STATEMENT
EXECUTE PROCEDURE refresh_configurationchoices_materialized_view();
"""

class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0058_auto_20170410_0957'),
    ]

    operations = [
        migrations.RunSQL(materialized_view),
    ]
