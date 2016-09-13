# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oilserver', '0032_configurationchoices_fix'),
    ]

    sql = """UPDATE oilserver_testcaseinstance
             SET testcaseinstancestatus_id = (SELECT id
                                              FROM oilserver_testcaseinstancestatus
                                              WHERE name = 'success')
             WHERE id IN (SELECT tci.id
                          FROM oilserver_testcase tc,
                               oilserver_testcaseinstance tci,
                               oilserver_pipeline p,
                               oilserver_build b,
                               oilserver_testcaseinstancestatus tcis,
                               oilserver_testcaseclass tcc,
                               oilserver_testframework tf
                          WHERE tc.id = tci.testcase_id
                          AND tci.build_id = b.id
                          AND b.pipeline_id = p.id
                          AND tci.testcaseinstancestatus_id = tcis.id
                          AND tc.testcaseclass_id = tcc.id
                          AND tcc.testframework_id = tf.id
                          AND tf.name = 'bundletests'
                          AND tcis.name = 'unknown'
                          AND tci.updated_at > TIMESTAMP '2016-07-18 00:00:00');
    """

    operations = [
        migrations.RunSQL(sql),
    ]
