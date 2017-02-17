# -*- coding: utf-8 -*-
import os
from django.db import migrations, transaction


def turn_off_tempest_plotting_and_change_description(apps, schema_editor):
    '''
    Make the tempest job no longer appear in the plots by default, and
    change description of bundlestests to accomodate tempest tests.
    '''

    JobType = apps.get_model('oilserver', 'JobType')
    with transaction.atomic():
        tempest_job = JobType.objects.get(name="test_tempest_smoke")
        tempest_job.plot = False
        tempest_job.save()
        tempest_job = JobType.objects.get(name="test_bundletests")
        tempest_job.description = "Run Openstack's Tempest Tests (Test Bundles)"
        tempest_job.save()


def noop():
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0048_rename_incorrectly_labelled_testframeworks'), ]

    operations = [migrations.RunPython(
        turn_off_tempest_plotting_and_change_description, reverse_code=noop), ]
