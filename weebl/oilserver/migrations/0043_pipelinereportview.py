# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0042_bugreportview'),
    ]
    sql = """
CREATE MATERIALIZED VIEW
    oilserver_pipelinereportview
AS WITH
    reportinfo AS (
        SELECT DISTINCT
            pipeline.id as pipeline_id,
            report.name as report_name
        FROM
            oilserver_pipeline pipeline,
            oilserver_jujuservicedeployment jujuservicedeployment,
            oilserver_unit unit,
            oilserver_machineconfiguration_productundertests machineconfiguration_productundertests,
            oilserver_productundertest productundertest,
            oilserver_productundertest productundertest2,
            oilserver_productundertest_reports productundertest_reports,
            oilserver_report report
        WHERE
            pipeline.id = jujuservicedeployment.pipeline_id AND
            jujuservicedeployment.id = unit.jujuservicedeployment_id AND
            unit.machineconfiguration_id = machineconfiguration_productundertests.machineconfiguration_id AND
            machineconfiguration_productundertests.productundertest_id = productundertest.id AND
            jujuservicedeployment.productundertest_id = productundertest2.id AND
            (
                productundertest.id = productundertest_reports.productundertest_id OR
                productundertest2.id = productundertest_reports.productundertest_id
            ) AND
            productundertest_reports.report_id = report.id
    ), environmentinfo AS (
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
    )
SELECT
    row_number() over() as id,
    reportinfo.report_name as reportname,
    date_trunc('day', pipeline.completed_at) as date,
    environmentinfo.environment_name as environmentname,
    COUNT(DISTINCT(pipeline.id)) as numpipelines,
    COUNT(CASE WHEN testcaseinstancestatus.name <> 'success' AND testcase.name = 'pipeline_deploy' THEN 1 END) as numdeployfail,
    COUNT(CASE WHEN testcaseinstancestatus.name <> 'success' AND testcase.name = 'pipeline_prepare' THEN 1 END) as numpreparefail,
    COUNT(CASE WHEN testcaseinstancestatus.name <> 'success' AND (testcase.name = 'test_bundletests' OR testcase.name = 'test_cloud_image') THEN 1 END) as numtestfail
FROM
    oilserver_pipeline pipeline,
    oilserver_build build,
    oilserver_testcaseinstance testcaseinstance,
    oilserver_testcaseinstancestatus testcaseinstancestatus,
    oilserver_testcase testcase,
    reportinfo,
    environmentinfo
WHERE
    pipeline.id = environmentinfo.pipeline_id AND
    pipeline.id = reportinfo.pipeline_id AND
    pipeline.completed_at IS NOT NULL AND
    pipeline.id = build.pipeline_id AND
    build.id = testcaseinstance.build_id AND
    testcaseinstancestatus.id = testcaseinstance.testcaseinstancestatus_id AND
    testcase.id = testcaseinstance.testcase_id
GROUP BY
    report_name,
    date,
    environment_name
;
    """

    operations = [
        migrations.RunSQL(sql),
        migrations.CreateModel(
            name='PipelineReportView',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('reportname', models.CharField(null=True, help_text='The name of the corresponding report.', max_length=255, blank=True)),
                ('date', models.DateTimeField(null=True, help_text='DateTime of these bugs.', blank=True, default=None)),
                ('environmentname', models.CharField(null=True, help_text='The name of the corresponding environment.', max_length=255, blank=True)),
                ('numpipelines', models.IntegerField(default=0, help_text='Number of pipelines.')),
                ('numdeployfail', models.IntegerField(default=0, help_text='Number of failed deploy stages.')),
                ('numpreparefail', models.IntegerField(default=0, help_text='Number of failed prepare stages.')),
                ('numtestfail', models.IntegerField(default=0, help_text='Number of failed test stages.')),
            ],
            options={
                'managed': False,
            },
        ),
    ]
