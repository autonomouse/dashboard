# -*- coding: utf-8 -*-
import os
from django.db import migrations, transaction


def rename_incorrectly_labelled_testframeworks(apps, schema_editor):
    '''Find testframeworks named "bundletests" or "cloud_image" and
    rename them "test_bundletests" and "test_cloud_image", respectively.'''
    TestFramework = apps.get_model('oilserver', 'TestFramework')
    with transaction.atomic():
        for bad_name in ["bundletests", "cloud_image"]:
            good_name = "test_" + bad_name
            for testframework in TestFramework.objects.all():
                if bad_name != testframework.name:
                    continue
                testframework.name = good_name
                testframework.save()


def noop():
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver',
         '0039_remove_oil_suffix_form_machines_and_merge'),
    ]

    operations = [
        migrations.RunPython(rename_incorrectly_labelled_testframeworks,
                             reverse_code=noop),
    ]
