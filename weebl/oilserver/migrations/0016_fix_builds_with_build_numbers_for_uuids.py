# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oilserver.utils
import uuid
from django.db.utils import IntegrityError


def fix_builds_with_build_numbers_for_uuids(apps, schema_editor):
    Build = apps.get_model('oilserver', 'Build')
    dodgy_builds = []
    for build in Build.objects.all():
        if len(build.uuid) == 36:
            continue
        build_id = build.uuid
        jobtype = build.jobtype
        if not Build.objects.filter(build_id=build_id, jobtype=jobtype).exists():
            build.build_id = build_id
            build.uuid = str(uuid.uuid4())
            build.save()
        else:
            build.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0015_auto_20160426_1053'),
    ]
    operations = [
        migrations.RunPython(
            fix_builds_with_build_numbers_for_uuids
        ),
    ]
