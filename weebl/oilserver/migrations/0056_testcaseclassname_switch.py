# -*- coding: utf-8 -*-
import re
from django.db import migrations, transaction


def testcaseclassname_switch(apps, schema_editor):
    pattern = r'(?P<testcase_name>.*Class) \((?P<testcaseclass_name>[^)]*)\)'
    TestCaseClass = apps.get_model('oilserver', 'TestCaseClass')
    TestCase = apps.get_model('oilserver', 'TestCase')
    with transaction.atomic():
        for blank_testcaseclass in TestCaseClass.objects.filter(name=''):
            testframework = blank_testcaseclass.testframework
            for testcase in TestCase.objects.filter(
                    testcaseclass=blank_testcaseclass):
                testcase_name = testcase.name
                match = re.match(pattern, testcase_name)
                if match:
                    regex_data = match.groupdict()
                    testcaseclass, _ = TestCaseClass.objects.get_or_create(
                        name=regex_data['testcaseclass_name'],
                        testframework=testframework
                    )
                    testcase.name = regex_data['testcase_name']
                    testcase.testcaseclass = testcaseclass
                    testcase.save()
            assert(len(TestCase.objects.filter(
                testcaseclass=blank_testcaseclass)) == 0)
            blank_testcaseclass.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0055_auto_20170404_1029'), ]

    operations = [migrations.RunPython(testcaseclassname_switch), ]
