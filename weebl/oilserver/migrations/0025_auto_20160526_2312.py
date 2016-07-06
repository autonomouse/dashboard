# -*- coding: utf-8 -*-
# pylint: disable=C0103

from __future__ import unicode_literals

from django.db import models, migrations
import oilserver.utils


def pipeline_softwareconfiguration_to_producttype(apps, schema_editor):
    p_models = ['SDN', 'Compute', 'BlockStorage', 'ImageStorage', 'Database']
    ProductUnderTest = apps.get_model('oilserver', 'ProductUnderTest')
    ProductType = apps.get_model('oilserver', 'ProductType')
    for model in p_models:
        params = {'name': model.lower(), 'toplevel': True}
        producttype = ProductType.objects.get_or_create(**params)[0]
        for model_object in apps.get_model('oilserver', model).objects.all():
            if model_object.name != 'default':
                product = ProductUnderTest.objects.get_or_create(
                    name=model_object.name)[0]
                product.producttype = producttype
                product.save()

    JujuServiceDeployment = apps.get_model('oilserver',
                                           'JujuServiceDeployment')
    Pipeline = apps.get_model('oilserver', 'Pipeline')
    for pipeline in Pipeline.objects.all():
        product_names = [getattr(pipeline, producttype.lower()).name
                         for producttype in p_models if
                         getattr(pipeline, producttype.lower()) != None]
        for product_name in product_names:
            product = ProductUnderTest.objects.get_or_create(
                name=product_name)[0]
            jujuservicedeployment = JujuServiceDeployment(
                productundertest=product,
                pipeline=pipeline
            )
            jujuservicedeployment.save()
            setattr(pipeline, product_name, None)
        pipeline.save()


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0024_auto_20160526_2010'),
    ]

    operations = [
        migrations.RunPython(
            pipeline_softwareconfiguration_to_producttype
        ),
    ]
