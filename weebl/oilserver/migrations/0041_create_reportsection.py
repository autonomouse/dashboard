# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import oilserver.utils


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0040_detailed_report_field_changes'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportSection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(null=True, help_text='DateTime this model instance was created.', blank=True, default=None)),
                ('updated_at', models.DateTimeField(help_text='DateTime this model instance was last updated.', default=oilserver.utils.time_now)),
                ('name', models.CharField(null=True, help_text='The section of detailed report.', blank=True, default=None, max_length=255)),
                ('functionalgroup', models.CharField(null=True, help_text='The functionality this subsection tests.', blank=True, default=None, max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='producttype',
            name='prettyname',
        ),
        migrations.RemoveField(
            model_name='testcaseclass',
            name='functionalgroup',
        ),
        migrations.AlterUniqueTogether(
            name='reportsection',
            unique_together=set([('name', 'functionalgroup')]),
        ),
        migrations.AddField(
            model_name='testcaseclass',
            name='reportsection',
            field=models.ForeignKey(null=True, related_name='testcaseclasses', to='oilserver.ReportSection'),
        ),
    ]
