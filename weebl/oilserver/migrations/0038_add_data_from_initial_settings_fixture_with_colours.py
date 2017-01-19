# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oilserver
from django.db.utils import IntegrityError
from django.db import transaction


def create_or_pass(model, name_description_dict, multiple):
    for name, description in name_description_dict.items():
        try:
            with transaction.atomic():
                params = {'name': name}
                for count, item in enumerate(description):
                    params[multiple[count]] = item
                new_instance = model(**params)
                new_instance.save()
        except IntegrityError:
            with transaction.atomic():
                existing_instance = model.objects.get(name=params['name'])
                for count, item in enumerate(description):
                    setattr(existing_instance, multiple[count], item)
                existing_instance.save()


def add_jobtype_data_from_initial_settings_fixture(apps, schema_editor):
    '''Add data from initial settings fixture, plus extra colour data.'''
    jt_name_descriptions = {
        "pipeline_start": ["Initialise test run", "2C001E", 0],
        "pipeline_deploy": ["Deploy Openstack", "772953", 1],
        "pipeline_prepare": ["Configure Openstack for test", "9F639A", 2],
        "test_tempest_smoke": ["Run Openstack's tempest tests", "DDC9D4", 3],
        "test_bundletests": ["Test Bundles", "FAD4C7", 4],
        "test_cloud_image": ["SSH to guest instance", "DEDBD8", 5] }
    create_or_pass(oilserver.models.JobType, jt_name_descriptions,
                   multiple=["description", "colour", "order"])


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0037_add_data_from_initial_settings_fixture'),
    ]
    operations = [
        migrations.AddField(
            model_name='jobtype',
            name='colour',
            field=models.CharField(default='56334b', help_text="HTML colour code for this job (excluding the '#' prefix).", max_length=6),
        ),
        migrations.AddField(
            model_name='jobtype',
            name='order',
            field=models.IntegerField(help_text='Order in which jobs are run/should be displayed in UI.', default=0),
        ),
        migrations.AddField(
            model_name='jobtype',
            name='plot',
            field=models.BooleanField(help_text='Show on plots (e.g. success rate and trends graphs).', default=True)
        ),
        migrations.RunPython(
            add_jobtype_data_from_initial_settings_fixture
        )
    ]
