# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('oilserver', '0015_auto_20160426_1053'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeeblSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('default_environment', models.ForeignKey(help_text='The default environment to display. If none, displays all.', blank=True, default=None, null=True, to='oilserver.Environment')),
                ('site', models.OneToOneField(help_text='To make sure there is only ever one instance per website.', to='sites.Site')),
            ],
        ),
    ]
