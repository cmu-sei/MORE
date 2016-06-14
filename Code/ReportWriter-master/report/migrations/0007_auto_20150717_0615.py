# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0006_auto_20150717_0544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='custom',
            field=models.CharField(max_length=16, null=True, blank=True),
        ),
    ]
