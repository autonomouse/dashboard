# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def get_or_create(model, params):
    if model.objects.filter(**params).exists():
        correct_model = model.objects.get(**params)
    else:
        correct_model = model(**params)
        correct_model.save()
    return correct_model

def get_or_create_correct_test_framework(TestFramework, jobtype):
    params = {'name': jobtype.name, 'version': 'notapplicable'}
    return get_or_create(TestFramework, params)

def get_or_create_correct_correct_testcaseclass(TestCaseClass, jobtype,
                                                test_framework):
    params = {'name': jobtype.name, 'testframework': test_framework}
    return get_or_create(TestCaseClass, params)

def get_or_create_correct_correct_testcase(TestCase, jobtype, testcaseclass):
    params = {'name': jobtype.name, 'testcaseclass': testcaseclass}
    return get_or_create(TestCase, params)

def remove_job_none_test_frameworks(apps, schema_editor):
    """This method finds testcaseinstances that have the build as the name of
    their test_framework (so "pipeline_deploy", for example) and "none" as
    their version (which would mean that the test_framework would be identified
    as "pipeline_deploy_none" in the above example). It then removes this and
    instead links it to the test_framework with "notapplicable" as the version
    (i.e. "pipeline_deploy_notapplicable").

    The reason for this is that the version field is only applicable for
    non-build (i.e. test) testframeworks, so we use "notapplicable" as the
    version for build testframeworks. However, in some earlier cases, "None"
    was mistakenly used (i.e. "pipeline_deploy_none"). This method finds and
    replaces them so that they all use the "notapplicable" as the version.

    """

    TestCaseInstance = apps.get_model('oilserver', 'TestCaseInstance')
    TestFramework = apps.get_model('oilserver', 'TestFramework')
    TestCaseClass = apps.get_model('oilserver', 'TestCaseClass')
    TestCase = apps.get_model('oilserver', 'TestCase')
    params = {'testcase__testcaseclass__testframework__version__isnull': True}
    for old_tci in TestCaseInstance.objects.filter(**params):
        build_id = old_tci.build.build_id
        jobtype = old_tci.build.jobtype
        pipeline = old_tci.build.pipeline
        status = old_tci.testcaseinstancestatus
        # N.B. returned_build is the same as what the weeblclient method
        # 'get_build_uuid_from_build_id_job_and_pipeline' fetches:
        returned_build = apps.get_model('oilserver', 'Build').objects.get(
            build_id=build_id, jobtype=jobtype, pipeline=pipeline)
        correct_test_framework = get_or_create_correct_test_framework(
            TestFramework, jobtype)
        correct_testcaseclass = get_or_create_correct_correct_testcaseclass(
            TestCaseClass, jobtype, correct_test_framework)
        correct_testcase = get_or_create_correct_correct_testcase(
            TestCase, jobtype, correct_testcaseclass)
        old_tci.delete()
        tci_params = {'build': returned_build,
                      'testcase': correct_testcase}
        testcaseinstance = get_or_create(TestCaseInstance, tci_params)
        testcaseinstance.testcaseinstancestatus = status
        testcaseinstance.save()
    TestCaseInstance.objects.filter(**params).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0018_auto_20160504_1015'),
    ]

    operations = [
        migrations.RunPython(
            remove_job_none_test_frameworks
        ),
    ]
