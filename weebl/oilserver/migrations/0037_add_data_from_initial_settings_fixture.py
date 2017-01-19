# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oilserver
from django.db.utils import IntegrityError
from django.db import transaction


def create_or_pass(model, name_description_dict):
    for name, description in name_description_dict.items():
        try:
            with transaction.atomic():
                new_instance = model(name=name, description=description)
                new_instance.save()
        except IntegrityError:
            pass


def set_up_statuses():
    ss_name_descriptions = {
        "unknown": "Current state of Jenkins is unknown.",
        "up": "Jenkins is functioning normally.",
        "unstable":
            "Jenkins is unstable suggesting that there may be a problem.",
        "down": "Jenkins is broken.", }
    create_or_pass(oilserver.models.ServiceStatus, ss_name_descriptions)


def set_up_testcaseinstancestatus():
    tcis_name_descriptions = {
        "unknown": "Current state of the build or test is unknown.",
        "success": "The build or test completed successfully.",
        "failure": "The build or test completed but was not successful.",
        "aborted": "The build or test was aborted.",
        "error": "The build or test was in error.",
        "skipped": "The build or test was skipped.", }
    create_or_pass(oilserver.models.TestCaseInstanceStatus, tcis_name_descriptions)


def add_data_from_initial_settings_fixture(apps, schema_editor):
    '''Add data from initial settings fixture.'''
    set_up_statuses()
    set_up_testcaseinstancestatus()


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0036_auto_20161207_1042'),
    ]
    operations = [
        migrations.RunPython(
            add_data_from_initial_settings_fixture
        ),
    ]
