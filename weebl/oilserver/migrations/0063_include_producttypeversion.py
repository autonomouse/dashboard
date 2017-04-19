# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, transaction, models
import oilserver
import oilserver.utils
from django.db.utils import IntegrityError


def make_PTV(product):
    branchname = product.name.split("_")[1]
    version = branchname.split("~")[0].split("-")[0].split("+")[0]
    if version.index('.'):
        if version[version.index('.'):] == '.0.0':
            version = version[:version.index('.')] + '.0'
    ptype = oilserver.models.ProductType.objects.get(
        name=product.producttype.name)
    with transaction.atomic():
        try:
            producttypeversion = oilserver.models.ProductTypeVersion(
                producttype=ptype, version=version)
            producttypeversion.save()
        except IntegrityError:
            pass

def include_producttypeversion(apps, schema_editor):
    ProductUnderTest = apps.get_model('oilserver', 'ProductUnderTest')
    maas_products = ProductUnderTest.objects.filter(
        producttype__name="maas")
    juju_products = ProductUnderTest.objects.filter(
        producttype__name="juju")
    for product in maas_products:
        make_PTV(product)
    for product in juju_products:
        make_PTV(product)

def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0062_auto_20170418_1536'), ]


    operations = [
        migrations.CreateModel(
            name='ProductTypeVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('created_at', models.DateTimeField(null=True, default=None, help_text='DateTime this model instance was created.', blank=True)),
                ('updated_at', models.DateTimeField(default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('version', models.CharField(unique=True, help_text='The version number of product.', max_length=255)),
                ('uuid', models.CharField(unique=True, default=oilserver.utils.generate_uuid, help_text='UUID of this type of product.', max_length=36)),
                ('producttype', models.ForeignKey(related_name='producttypeversions', to='oilserver.ProductType', null=True, blank=True, default=None)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='productundertest',
            name='producttypeversion',
            field=models.ForeignKey(default=None, related_name='productundertests', blank=True, null=True, to='oilserver.ProductTypeVersion'),
        ),
        migrations.AddField(
            model_name='release',
            name='actualrelease',
            field=models.BooleanField(default=False, help_text='This was the actual release of the product.'),
        ),
        migrations.AddField(
            model_name='release',
            name='producttypeversion',
            field=models.ForeignKey(default=None, related_name='releases', blank=True, null=True, to='oilserver.ProductTypeVersion'),
        ),
        migrations.AddField(
            model_name='release',
            name='releasedate',
            field=models.DateField(default=None, blank=True, null=True, help_text='Date the pipeline was completed.'),
        ),
        migrations.AddField(
            model_name='release',
            name='releasetype',
            field=models.ForeignKey(default=None, related_name='releases', blank=True, null=True, to='oilserver.ReleaseType'),
        ),
        migrations.AlterField(
            model_name='releasetype',
            name='name',
            field=models.CharField(default='final', max_length=255, unique=True, help_text='The type of release.'),
        ),
        migrations.RunPython(
            include_producttypeversion, reverse_code=noop),
        ]
