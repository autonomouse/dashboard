# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from oilserver.models import TestCaseInstanceStatus

def add_skipped_testcaseinstancestatus(apps, schema_editor):
    ''' Add the "skipped" status to the testcaseinstancestatus.'''
    skipped = TestCaseInstanceStatus(name='skipped',
                                     description='The build or test was skipped.')
    skipped.save()
    return skipped


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0029_auto_20160614_1636'),
    ]
    operations = [
        migrations.RunPython(
            add_skipped_testcaseinstancestatus
        ),
    ]
