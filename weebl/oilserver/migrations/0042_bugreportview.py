# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0041_create_reportsection'),
    ]
    sql = """
CREATE MATERIALIZED VIEW
    oilserver_bugreportview
AS SELECT
    row_number() over() as id,
    reportR.name as reportname,
    date_trunc('day', pipeline.completed_at) as date,
    environment.name as environmentname,
    reportsection.name as groupname,
    bug.id as bug_id,
    COUNT(DISTINCT(bugoccurrence.id)) as occurrences
FROM
    oilserver_bug bug,
    oilserver_bugoccurrence bugoccurrence,
    oilserver_knownbugregex knownbugregex,
    oilserver_testcaseinstance testcaseinstance,
    oilserver_build buildR,
    oilserver_pipeline pipelineR,
    oilserver_jujuservicedeployment jujuservicedeploymentR,
    oilserver_unit unitR,
    oilserver_machineconfiguration machineconfigurationR,
    oilserver_machineconfiguration_productundertests machineconfiguration_productundertestsR,
    oilserver_productundertest productundertestR,
    oilserver_productundertest productundertestR2,
    oilserver_productundertest_reports productundertest_reportsR,
    oilserver_report reportR,
    oilserver_testcase testcase,
    oilserver_build build,
    oilserver_pipeline pipeline,
    oilserver_buildexecutor buildexecutor,
    oilserver_jenkins jenkins,
    oilserver_environment environment,
    oilserver_testcaseclass testcaseclass LEFT OUTER JOIN oilserver_reportsection reportsection ON (reportsection_id = reportsection.id)
WHERE
    bug.id = knownbugregex.bug_id AND
    knownbugregex.id = bugoccurrence.knownbugregex_id AND
    bugoccurrence.testcaseinstance_id = testcaseinstance.id AND
    testcaseinstance.testcase_id = testcase.id AND
    testcase.testcaseclass_id = testcaseclass.id AND
    testcaseinstance.build_id = build.id AND
    build.pipeline_id = pipeline.id AND
    pipeline.completed_at IS NOT NULL AND
    pipeline.buildexecutor_id = buildexecutor.id AND
    buildexecutor.jenkins_id = jenkins.id AND
    jenkins.environment_id = environment.id AND
    (
        testcaseinstance.build_id = buildR.id AND
        buildR.pipeline_id = pipelineR.id AND
        pipelineR.id = jujuservicedeploymentR.pipeline_id AND
        jujuservicedeploymentR.id = unitR.jujuservicedeployment_id AND
        unitR.machineconfiguration_id = machineconfigurationR.id AND
        machineconfiguration_productundertestsR.machineconfiguration_id = machineconfigurationR.id AND
        machineconfiguration_productundertestsR.productundertest_id = productundertestR.id AND
        jujuservicedeploymentR.productundertest_id = productundertestR2.id AND
        (productundertestR.id = productundertest_reportsR.productundertest_id OR
         productundertestR2.id = productundertest_reportsR.productundertest_id) AND
        productundertest_reportsR.report_id = reportR.id
    )
GROUP BY reportname, date, environmentname, groupname, bug.id
WITH NO DATA;
    """

    operations = [
        migrations.RunSQL(sql),
        migrations.CreateModel(
            name='BugReportView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('reportname', models.CharField(null=True, help_text='The name of the corresponding report.', blank=True, max_length=255)),
                ('date', models.DateTimeField(null=True, default=None, help_text='DateTime of these bugs.', blank=True)),
                ('environmentname', models.CharField(null=True, help_text='The name of the corresponding environment.', blank=True, max_length=255)),
                ('groupname', models.CharField(null=True, help_text='The name of the corresponding group.', blank=True, max_length=255)),
                ('occurrences', models.IntegerField(default=0, help_text='Number of occurrences of the bug.')),
            ],
            options={
                'managed': False,
            },
        ),
    ]
