# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0008_issuereport'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='osr_pattern_type',
            field=models.CharField(default=b'ubiquitous', max_length=32, null=True, verbose_name=b'Overlooked security requirements pattern type', choices=[(b'ubiquitous', b'Ubiquitous'), (b'event-driven', b'Event-Driven'), (b'unwanted behavior', b'Unwanted Behavior'), (b'state-driven', b'State-Driven')]),
        ),
    ]
