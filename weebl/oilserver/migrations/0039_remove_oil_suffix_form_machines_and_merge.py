# -*- coding: utf-8 -*-
import os
from django.db import migrations, transaction


def remove_oil_suffix_from_machines_and_merge(apps, schema_editor):
    '''Find machines that end in a .oil suffix and merge them with the real one
    (i.e. the one without the .oil).'''

    with transaction.atomic():
        Machine = apps.get_model('oilserver', 'Machine')
        MachineConfiguration = apps.get_model(
            'oilserver', 'MachineConfiguration')
        oily_machines = [machine for machine in Machine.objects.all() if '.' in
                         machine.hostname] # (to find *.oil and *.oilstaging)
        for machine_oil in oily_machines:
            correct_machine_name = os.path.splitext(machine_oil.hostname)[0]
            [correct_machine, _] = Machine.objects.get_or_create(
                hostname=correct_machine_name)
            incorrect_machine_configs = MachineConfiguration.objects.filter(
                machine=machine_oil)
            for bad_config in incorrect_machine_configs:
                bad_config.machine = correct_machine
                bad_config.save()
            machine_oil.delete()


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver',
         '0038_add_data_from_initial_settings_fixture_with_colours'),
    ]

    operations = [
        migrations.RunPython(remove_oil_suffix_from_machines_and_merge,
                             reverse_code=noop),
    ]
