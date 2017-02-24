# -*- coding: utf-8 -*-
import os
from django.db import migrations, transaction


def set_jobtype_data(JobType, order, name, description, colour, plot):
    if JobType.objects.filter(name=name).exists():
        tempest_job = JobType.objects.get(name=name)
        tempest_job.plot = description
        tempest_job.plot = colour
        tempest_job.plot = order
        tempest_job.plot = plot
        tempest_job.save()


def amend_jobtype_descriptions_and_colours(apps, schema_editor):
    JobType = apps.get_model('oilserver', 'JobType')
    with transaction.atomic():
        set_jobtype_data(JobType, 0, "pipeline_start", "Initialise test run",
                         "DEDBD8", False)
        set_jobtype_data(JobType, 1, "pipeline_deploy", "Deploy Openstack",
                         "84377D", True)
        set_jobtype_data(JobType, 2, "pipeline_prepare", "Configure Openstack",
                         "9F639A", True)
        set_jobtype_data(JobType, 3, "test_tempest_smoke", "Tempest (old)",
                         "FAD4C7", False)
        set_jobtype_data(JobType, 4, "test_bundletests", "Tempest", "806678",
                         True)
        set_jobtype_data(JobType, 5, "test_juju_bootstrap",
                         "OpenStack Provider", "56334B", True)
        set_jobtype_data(JobType, 6, "test_cloud_image",
                         "SSH to guest instance", "2C001E", True)

def noop():
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0051_configurationchoices_fix_for_extra_toplevel_products'), ]

    operations = [migrations.RunPython(
        amend_jobtype_descriptions_and_colours, reverse_code=noop), ]
