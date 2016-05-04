# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oilserver.utils
from django.db.utils import IntegrityError

def remove_superfluous_bugoccurrences(BugOccurrence, bugoccurrences, keep):
    superfluous_bugoccurrences = []
    for bugoccurrence in bugoccurrences:
        exists = BugOccurrence.objects.filter(
            testcaseinstance=keep, regex=bugoccurrence.regex).exists()
        if not exists:
            bugoccurrence.testcaseinstance = keep
            bugoccurrence.save()
        else:
            superfluous_bugoccurrences.append(bugoccurrence)
    for bugoccurrence in superfluous_bugoccurrences:
       bugoccurrence.delete()

def merge_duplicate_test_case_instances(TCIStatus, default_test_case_instance,
                                        duplicate_testcaseinstances,
                                        BugOccurrence):
    ''' Merges the duplicated testcaseinstances together. '''
    keep = default_test_case_instance
    bugoccurrences = []
    testcaseinstancestatuses = []
    for test_case_instance in duplicate_testcaseinstances:
        bugoccurrences.extend(test_case_instance.bugoccurrence_set.all())
        testcaseinstancestatuses.append(
            test_case_instance.testcaseinstancestatus)
    remove_superfluous_bugoccurrences(BugOccurrence, bugoccurrences, keep)
    statuses = [testcaseinstancestatus.name for testcaseinstancestatus in
                testcaseinstancestatuses]
    if "failure" in statuses:
        statusname = "failure"
    elif "error" in statuses:
        statusname = "error"
    elif "success" in statuses:
        statusname = "success"
    elif "aborted" in statuses:
        statusname = "aborted"
    else:
        statusname = "unknown"
    keep.testcaseinstancestatus = TCIStatus.objects.get(name=statusname)
    keep.save()
    return keep

def remove_duplicate_testcaseinstances(apps, schema_editor):
    Build = apps.get_model('oilserver', 'Build')
    TestCaseInstance = apps.get_model('oilserver', 'TestCaseInstance')
    TCIStatus = apps.get_model('oilserver', 'TestCaseInstanceStatus')
    BugOccurrence = apps.get_model('oilserver', 'BugOccurrence')
    duplicate_testcaseinstances_to_remove = []
    for build in Build.objects.all():
        test_case_instances = TestCaseInstance.objects.filter(
            build__uuid=build.uuid)
        testcases = [test_case_instance.testcase for test_case_instance in
                     test_case_instances]
        if len(set(testcases)) == len(testcases):
            continue
        for test_case_instance in test_case_instances:
            if testcases.count(test_case_instance.testcase) == 1:
                continue
            if test_case_instance in duplicate_testcaseinstances_to_remove:
                continue
            duplicate_testcases = [
                tc for tc in testcases if tc==test_case_instance.testcase]
            duplicate_testcaseinstances = [ti for ti in test_case_instances if
                                           ti.testcase in duplicate_testcases]
            keep = merge_duplicate_test_case_instances(
                TCIStatus, test_case_instance, duplicate_testcaseinstances,
                BugOccurrence)
            index = duplicate_testcaseinstances.index(keep)
            duplicate_testcaseinstances.pop(index)
            duplicate_testcaseinstances_to_remove.extend(
                duplicate_testcaseinstances)

    # Remove:
    for duplicate_testcaseinstance in duplicate_testcaseinstances_to_remove:
        duplicate_testcaseinstance.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0016_fix_builds_with_build_numbers_for_uuids'),
    ]
    operations = [
        migrations.RunPython(
            remove_duplicate_testcaseinstances
        ),
    ]
