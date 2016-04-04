# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import oilserver.utils

def get_or_create_new_model(Model, key, get_params_dict, new_params_dict):
    model_key_values = []
    for model in Model.objects.all():
        model_key_values.append(model.__dict__[key])
    if (get_params_dict['name'] not in model_key_values):
        new_model = Model(**new_params_dict)
        new_model.save()
    return Model.objects.get(**get_params_dict)

def link_bugoccurrence_to_testcaseinstance(build, BugOccurrence,
                                           testcaseinstance):
    for bugoccurrence in BugOccurrence.objects.filter(build=build):
        bugoccurrence.testcaseinstance = testcaseinstance
        bugoccurrence.save()

def buildstatus_to_testcaseinstancestatus(apps, schema_editor):

    BuildStatus = apps.get_model('oilserver', 'BuildStatus')
    JobType = apps.get_model('oilserver', 'JobType')
    TestCaseInstance = apps.get_model('oilserver', 'TestCaseInstance')
    BugOccurrence = apps.get_model('oilserver', 'BugOccurrence')

    for status in BuildStatus.objects.all():
        testcaseinstancestatus = get_or_create_new_model(
            apps.get_model('oilserver', 'TestCaseInstanceStatus'),
            'name',
            {'name': status.name},
            {'name': status.name, 'description': status.description})

        for build in status.build_set.all():
            jobtype = JobType.objects.get(name=build.jobtype.name)

            testframework = get_or_create_new_model(
                apps.get_model('oilserver', 'TestFramework'),
                'name',
                {'name': jobtype.name},
                {'name': jobtype.name})

            testcaseclass = get_or_create_new_model(
                apps.get_model('oilserver', 'TestCaseClass'),
                'name',
                {'name': jobtype.name},
                {'name': jobtype.name, 'testframework': testframework})

            testcase = get_or_create_new_model(
                apps.get_model('oilserver', 'TestCase'),
                'name',
                {'name': jobtype.name},
                {'name': jobtype.name, 'testcaseclass': testcaseclass})

            testcaseinstance = TestCaseInstance(
                testcaseinstancestatus=testcaseinstancestatus,
                build=build,
                testcase=testcase)
            testcaseinstance.save()

            link_bugoccurrence_to_testcaseinstance(
                build, BugOccurrence, testcaseinstance)


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0007_auto_20160308_1640'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created_at', models.DateTimeField(blank=True, default=None, null=True, help_text='DateTime this model instance was created.')),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('name', models.CharField(unique=True, max_length=255, help_text='Name of this individual test case.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestCaseClass',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created_at', models.DateTimeField(blank=True, default=None, null=True, help_text='DateTime this model instance was created.')),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('name', models.CharField(unique=True, max_length=255, help_text='Name of this individual test case.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestCaseInstance',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('uuid', models.CharField(unique=True, max_length=36, default=oilserver.utils.generate_uuid, help_text='UUID of this TestCase.')),
                ('build', models.ForeignKey(blank=True, to='oilserver.Build', null=True, default=None)),
                ('testcase', models.ForeignKey(blank=True, to='oilserver.TestCase', null=True, default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestCaseInstanceStatus',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, default='unknown', help_text='The resulting outcome of the test.')),
                ('description', models.TextField(blank=True, default=None, null=True, help_text='Optional description for outcome.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TestFramework',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created_at', models.DateTimeField(blank=True, default=None, null=True, help_text='DateTime this model instance was created.')),
                ('updated_at', models.DateTimeField(auto_now_add=True, default=oilserver.utils.time_now, help_text='DateTime this model instance was last updated.')),
                ('name', models.CharField(unique=True, max_length=255, help_text='Name of the testing framework.')),
                ('description', models.TextField(blank=True, default=None, null=True, help_text='Optional description for this test framework.')),
                ('version', models.TextField(blank=True, default=None, null=True, help_text='Version of this test framework.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='testcaseinstance',
            name='testcaseinstancestatus',
            field=models.ForeignKey(blank=True, to='oilserver.TestCaseInstanceStatus', null=True, default=None),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testcaseclass',
            name='testframework',
            field=models.ForeignKey(blank=True, to='oilserver.TestFramework', null=True, default=None),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='testcase',
            name='testcaseclass',
            field=models.ForeignKey(blank=True, to='oilserver.TestCaseClass', null=True, default=None),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bugoccurrence',
            name='testcaseinstance',
            field=models.ForeignKey(blank=True, to='oilserver.TestCaseInstance', null=True, default=None),
            preserve_default=True,
        ),
        migrations.RunPython(
            buildstatus_to_testcaseinstancestatus
        ),
        migrations.RemoveField(
            model_name='build',
            name='buildstatus',
        ),
        migrations.DeleteModel(
            name='BuildStatus',
        ),
        migrations.AlterUniqueTogether(
            name='bugoccurrence',
            unique_together=set([('testcaseinstance', 'regex')]),
        ),
        migrations.RemoveField(
            model_name='bugoccurrence',
            name='build',
        ),
    ]
