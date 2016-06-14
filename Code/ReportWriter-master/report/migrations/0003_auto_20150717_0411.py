# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0002_report_custom'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='custom',
            field=models.CharField(default=b'none', max_length=16, null=True, verbose_name=b'Author has written a custom MUO', blank=True),
        ),
    ]
