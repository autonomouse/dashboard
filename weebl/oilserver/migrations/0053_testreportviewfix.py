# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0052_pipelinereportviewfix'),
    ]
    sql = """
DROP MATERIALIZED VIEW oilserver_testreportview;
CREATE MATERIALIZED VIEW
    oilserver_testreportview
AS WITH
    testcaseinfo AS (
        SELECT
            testcaseinstance.id as testcaseinstance_id,
            testcase.name as testcase_name,
            testcase.id as testcase_id,
            testcaseclass.name as testcaseclass_name,
            testcaseclass.id as testcaseclass_id,
            testframework.name as testframework_name
        FROM
            oilserver_testcaseinstance testcaseinstance,
            oilserver_testcase testcase,
            oilserver_testcaseclass testcaseclass,
            oilserver_testframework testframework
        WHERE
            testcaseinstance.testcase_id = testcase.id AND
            testcase.testcaseclass_id = testcaseclass.id AND
            testcaseclass.testframework_id = testframework.id
    ), buginfo AS (
        SELECT DISTINCT ON (testcase_id)
            testcase.id as testcase_id,
            bug.id as bug_id,
            COUNT(bugoccurrence.id) as bugoccurrences
        FROM
            oilserver_testcaseinstance testcaseinstance,
            oilserver_testcase testcase,
            oilserver_bugoccurrence bugoccurrence,
            oilserver_knownbugregex knownbugregex,
            oilserver_bug bug
        WHERE
            testcaseinstance.id = bugoccurrence.testcaseinstance_id AND
            bugoccurrence.knownbugregex_id = knownbugregex.id AND
            knownbugregex.bug_id = bug.id AND
            testcaseinstance.testcase_id = testcase.id
        GROUP BY
            bug.id,
            testcase.id
        ORDER BY
            testcase_id, bugoccurrences DESC
    ), reportinfo AS (
        SELECT DISTINCT
            testcaseinstance.id as testcaseinstance_id,
            report.name as report_name
        FROM
            oilserver_testcaseinstance testcaseinstance,
            oilserver_testcase testcase,
            oilserver_testcaseclass_producttypes testcaseclass_producttypes,
            oilserver_build build,
            oilserver_pipeline pipeline,
            oilserver_jujuservicedeployment jujuservicedeployment,
            oilserver_unit unit,
            oilserver_machineconfiguration_productundertests machineconfiguration_productundertests,
            oilserver_productundertest productundertest,
            oilserver_productundertest productundertest2,
            oilserver_productundertest_reports productundertest_reports,
            oilserver_report report
        WHERE
            testcaseinstance.build_id = build.id AND
            testcaseinstance.testcase_id = testcase.id AND
            testcase.testcaseclass_id = testcaseclass_producttypes.testcaseclass_id AND
            build.pipeline_id = pipeline.id AND
            pipeline.id = jujuservicedeployment.pipeline_id AND
            jujuservicedeployment.id = unit.jujuservicedeployment_id AND
            unit.machineconfiguration_id = machineconfiguration_productundertests.machineconfiguration_id AND
            machineconfiguration_productundertests.productundertest_id = productundertest.id AND
            jujuservicedeployment.productundertest_id = productundertest2.id AND
            testcaseclass_producttypes.producttype_id = productundertest2.producttype_id AND
            (
                productundertest.id = productundertest_reports.productundertest_id OR
                productundertest2.id = productundertest_reports.productundertest_id
            ) AND
            productundertest_reports.report_id = report.id
    ), environmentinfo AS (
        SELECT
            pipeline.id as pipeline_id,
            environment.name as environment_name,
            openstackversion.name as openstackversion_name,
            ubuntuversion.name as ubuntuversion_name
        FROM
            oilserver_pipeline pipeline,
            oilserver_versionconfiguration versionconfiguration,
            oilserver_openstackversion openstackversion,
            oilserver_ubuntuversion ubuntuversion,
            oilserver_buildexecutor buildexecutor,
            oilserver_jenkins jenkins,
            oilserver_environment environment
        WHERE
            pipeline.versionconfiguration_id = versionconfiguration.id AND
            versionconfiguration.openstackversion_id = openstackversion.id AND
            versionconfiguration.ubuntuversion_id = ubuntuversion.id AND
            pipeline.buildexecutor_id = buildexecutor.id AND
            buildexecutor.jenkins_id = jenkins.id AND
            jenkins.environment_id = environment.id
    ), groupinfo AS (
        SELECT
            testcaseclass.id as testcaseclass_id,
            reportsection.name as group_name,
            reportsection.functionalgroup as subgroup
        FROM
            oilserver_testcaseclass testcaseclass,
            oilserver_reportsection reportsection
        WHERE
            testcaseclass.reportsection_id = reportsection.id
    ), testinfo AS (
        SELECT
            pipeline.id as pipeline_id,
            testcaseinstance.id as testcaseinstance_id,
            testcase.id as testcase_id,
            CASE WHEN testcaseinstancestatus.name = 'success' THEN 1 END as testcaseinstance_pass,
            CASE WHEN testcaseinstancestatus.name = 'skipped' THEN 1 END as testcaseinstance_skip,
            CASE WHEN testcaseinstancestatus.name <> 'success' AND testcaseinstancestatus.name <> 'skipped' THEN 1 END as testcaseinstance_fail
        FROM
            oilserver_pipeline pipeline,
            oilserver_build build,
            oilserver_testcaseinstance testcaseinstance,
            oilserver_testcaseinstancestatus testcaseinstancestatus,
            oilserver_testcase testcase
        WHERE
            pipeline.id = build.pipeline_id AND
            testcaseinstance.build_id = build.id AND
            testcaseinstance.testcase_id = testcase.id AND
            testcaseinstance.testcaseinstancestatus_id = testcaseinstancestatus.id
    )
SELECT
    row_number() over() as id,
    reportinfo.report_name as reportname,
    date_trunc('day', pipeline.completed_at) as date,
    environmentinfo.environment_name as environmentname,
    environmentinfo.openstackversion_name as openstackversionname,
    environmentinfo.ubuntuversion_name as ubuntuversionname,
    groupinfo.group_name as groupname,
    groupinfo.subgroup as subgroupname,
    testcaseinfo.testcase_name as testcasename,
    testcaseinfo.testcaseclass_name as testcaseclassname,
    testcaseinfo.testframework_name as testframeworkname,
    buginfo.bug_id as bug_id,
    COUNT(DISTINCT(testcaseinfo.testcaseinstance_id)) as numtestcases,
    COUNT(testinfo.testcaseinstance_pass) as numsuccess,
    COUNT(testinfo.testcaseinstance_skip) as numskipped,
    COUNT(testinfo.testcaseinstance_fail) as numfailed
FROM
    testcaseinfo LEFT OUTER JOIN groupinfo USING (testcaseclass_id) LEFT OUTER JOIN buginfo USING (testcase_id),
    oilserver_testcaseinstance testcaseinstance,
    oilserver_build build,
    oilserver_pipeline pipeline,
    environmentinfo,
    reportinfo,
    testinfo
WHERE
    testinfo.testcaseinstance_id = testcaseinfo.testcaseinstance_id AND
    testcaseinfo.testcaseinstance_id = reportinfo.testcaseinstance_id AND
    testcaseinfo.testcaseinstance_id = testcaseinstance.id AND
    testcaseinstance.build_id = build.id AND
    build.pipeline_id = pipeline.id AND
    pipeline.completed_at IS NOT NULL AND
    pipeline.id = environmentinfo.pipeline_id AND
    testinfo.pipeline_id = pipeline.id
GROUP BY
    reportname,
    date,
    environmentname,
    openstackversionname,
    ubuntuversionname,
    groupname,
    subgroupname,
    testcasename,
    testcaseclassname,
    testframeworkname,
    bug_id
WITH NO DATA;
    """

    operations = [
        migrations.RunSQL(sql),
    ]
