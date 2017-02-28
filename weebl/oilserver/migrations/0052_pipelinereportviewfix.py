# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0051_auto_20170228_1116'),
    ]
    sql = """
DROP MATERIALIZED VIEW oilserver_pipelinereportview;
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
            environment.name as environment_name,
            CASE WHEN COUNT(DISTINCT(testcaseinstance)) <= COUNT(DISTINCT(build)) THEN TRUE ELSE FALSE END as failed_testing
        FROM
            oilserver_pipeline pipeline,
            oilserver_build build,
            oilserver_testcaseinstance testcaseinstance,
            oilserver_buildexecutor buildexecutor,
            oilserver_jenkins jenkins,
            oilserver_environment environment
        WHERE
            pipeline.buildexecutor_id = buildexecutor.id AND
            buildexecutor.jenkins_id = jenkins.id AND
            jenkins.environment_id = environment.id AND
            pipeline.id = build.pipeline_id AND
            testcaseinstance.build_id = build.id
        GROUP BY
            pipeline.id,
            environment.name
    )
SELECT
    row_number() over() as id,
    reportinfo.report_name as reportname,
    date_trunc('day', pipeline.completed_at) as date,
    environmentinfo.environment_name as environmentname,
    COUNT(DISTINCT(pipeline.id)) as numpipelines,
    COUNT(CASE WHEN testcaseinstancestatus.name <> 'success' AND testcase.name = 'pipeline_deploy' THEN 1 END) as numdeployfail,
    COUNT(CASE WHEN testcaseinstancestatus.name <> 'success' AND testcase.name = 'pipeline_prepare' THEN 1 END) as numpreparefail,
    COUNT(CASE WHEN environmentinfo.failed_testing AND testcase.name = 'test_bundletests' THEN 1 END) as numtestfail
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
    ]
