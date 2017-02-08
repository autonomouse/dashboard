# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0039_remove_oil_suffix_form_machines_and_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='jujuservicedeployment',
            name='success',
            field=models.BooleanField(default=True, help_text='Whether this juju service deployed successfully.'),
        ),
        migrations.AddField(
            model_name='producttype',
            name='prettyname',
            field=models.CharField(blank=True, default=None, null=True, help_text='Pretty name of the type of product.', unique=True, max_length=255),
        ),
        migrations.AddField(
            model_name='testcaseclass',
            name='functionalgroup',
            field=models.CharField(blank=True, default=None, null=True, max_length=255, help_text='The functionality this class tests.'),
        ),
        migrations.AddField(
            model_name='testcaseclass',
            name='producttypes',
            field=models.ManyToManyField(blank=True, default=None, null=True, to='oilserver.ProductType', help_text='Product types this class tests.', related_name='testcaseclasses'),
        ),
        migrations.AlterField(
            model_name='testcaseclass',
            name='name',
            field=models.CharField(help_text='Name of this individual test case class.', max_length=255),
        ),
    ]
