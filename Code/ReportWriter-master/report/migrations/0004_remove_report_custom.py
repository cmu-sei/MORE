# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0003_auto_20150717_0411'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='custom',
        ),
    ]
