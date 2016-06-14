# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0022_auto_20150703_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuereport',
            name='resolve_reason',
            field=models.TextField(default=b'/', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='issuereport',
            name='reviewed_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='issuereport',
            name='status',
            field=models.CharField(default=b'open', max_length=64, db_index=True, choices=[(b'open', b'Open'), (b'investigating', b'Investigating'), (b'reopened', b'Re-opened'), (b'resolved', b'Resolved')]),
        ),
    ]
