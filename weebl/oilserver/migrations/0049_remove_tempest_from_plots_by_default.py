# -*- coding: utf-8 -*-
import os
from django.db import migrations, transaction


def turn_off_tempest_plotting(apps, schema_editor):
    '''
    Make the tempest job no longer appear in the plots by default.
    '''

    JobType = apps.get_model('oilserver', 'JobType')
    with transaction.atomic():
        if JobType.objects.filter(name='test_tempest_smoke').exists():
            tempest_job = JobType.objects.get(name="test_tempest_smoke")
            tempest_job.plot = False
            tempest_job.save()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0048_rename_incorrectly_labelled_testframeworks'), ]

    operations = [migrations.RunPython(
        turn_off_tempest_plotting, reverse_code=noop), ]
