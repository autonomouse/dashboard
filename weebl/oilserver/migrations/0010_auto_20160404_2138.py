# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


def gen_uuid_model(model):
    for row in model.objects.all():
        row.uuid = uuid.uuid4()
        row.save()


def gen_uuids(apps, schema_editor):
    model_names = ['TestFramework', 'TestCase', 'TestCaseClass']
    for model_name in model_names:
       model = apps.get_model('oilserver', model_name)
       gen_uuid_model(model)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0009_auto_20160329_0837'),
    ]

    operations = [
        migrations.RunPython(gen_uuids, reverse_code=noop),
    ]
