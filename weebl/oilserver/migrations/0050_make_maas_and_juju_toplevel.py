# -*- coding: utf-8 -*-
import os
from django.db import migrations, transaction


def make_maas_and_juju_toplevel(apps, schema_editor):
    ProductType = apps.get_model('oilserver', 'ProductType')
    with transaction.atomic():
        if ProductType.objects.filter(name='maas').exists():
            maas_product = ProductType.objects.get(name='maas')
            maas_product.toplevel = True
            maas_product.save()
        if ProductType.objects.filter(name='juju').exists():
            juju_product = ProductType.objects.get(name='juju')
            juju_product.toplevel = True
            juju_product.save()


def noop():
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0049_remove_tempest_from_plots_by_default'),
    ]

    operations = [
        migrations.RunPython(make_maas_and_juju_toplevel, reverse_code=noop),
    ]
