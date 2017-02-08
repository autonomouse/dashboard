# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0043_pipelinereportview'),
    ]
    sql = """
CREATE MATERIALIZED VIEW
    oilserver_servicereportview
AS WITH
    environmentinfo AS (
        SELECT
            pipeline.id as pipeline_id,
            environment.name as environment_name
        FROM
            oilserver_pipeline pipeline,
            oilserver_buildexecutor buildexecutor,
            oilserver_jenkins jenkins,
            oilserver_environment environment
        WHERE
            pipeline.buildexecutor_id = buildexecutor.id AND
            buildexecutor.jenkins_id = jenkins.id AND
            jenkins.environment_id = environment.id
    ), serviceinfo AS (
        SELECT
            pipeline.id as pipeline_id,
            report.name as report_name,
            producttype.name as producttype_name,
            productundertest.name as productundertest_name,
            BOOL_AND(jujuservicedeployment.success) as success
        FROM
            oilserver_pipeline pipeline,
            oilserver_jujuservicedeployment jujuservicedeployment,
            oilserver_unit unit,
            oilserver_machineconfiguration_productundertests machineconfiguration_productundertests,
            oilserver_productundertest productundertest,
            oilserver_productundertest productundertest2,
            oilserver_productundertest_reports productundertest_reports,
            oilserver_producttype producttype,
            oilserver_report report
        WHERE
            jujuservicedeployment.pipeline_id = pipeline.id AND
            jujuservicedeployment.id = unit.jujuservicedeployment_id AND
            unit.machineconfiguration_id = machineconfiguration_productundertests.machineconfiguration_id AND
            machineconfiguration_productundertests.productundertest_id = productundertest2.id AND
            jujuservicedeployment.productundertest_id = productundertest.id AND
            (
                productundertest.id = productundertest_reports.productundertest_id OR
                productundertest2.id = productundertest_reports.productundertest_id
            ) AND
            productundertest.producttype_id = producttype.id AND
            productundertest_reports.report_id = report.id
        GROUP BY
            pipeline.id,
            productundertest.name,
            producttype.name,
            success,
            report.name
        ORDER BY
            pipeline.id
    )
SELECT
    row_number() over() as id,
    serviceinfo.report_name as reportname,
    date_trunc('day', pipeline.completed_at) as date,
    environmentinfo.environment_name as environmentname,
    COUNT(DISTINCT(pipeline.id)) as numpipelines,
    serviceinfo.producttype_name as producttypename,
    serviceinfo.productundertest_name as productundertestname,
    COUNT(CASE WHEN serviceinfo.success = TRUE THEN 1 END) as numsuccess
FROM
    oilserver_pipeline pipeline,
    serviceinfo,
    environmentinfo
WHERE
    pipeline.id = serviceinfo.pipeline_id AND
    pipeline.completed_at IS NOT NULL AND
    pipeline.id = environmentinfo.pipeline_id
GROUP BY
    reportname,
    date,
    environmentname,
    producttypename,
    productundertestname
;
    """

    operations = [
        migrations.RunSQL(sql),
        migrations.CreateModel(
            name='ServiceReportView',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('reportname', models.CharField(null=True, blank=True, max_length=255, help_text='The name of the corresponding report.')),
                ('date', models.DateTimeField(null=True, blank=True, default=None, help_text='DateTime of these bugs.')),
                ('environmentname', models.CharField(null=True, blank=True, max_length=255, help_text='The name of the corresponding environment.')),
                ('numpipelines', models.IntegerField(default=0, help_text='Number of pipelines.')),
                ('producttypename', models.CharField(null=True, blank=True, max_length=255, help_text='The name of the corresponding producttype.')),
                ('productundertestname', models.CharField(null=True, blank=True, max_length=255, help_text='The name of the corresponding productundertest.')),
                ('numsuccess', models.IntegerField(default=0, help_text='Number of successful deploys for the productundertest.')),
            ],
            options={
                'managed': False,
            },
        ),
    ]
