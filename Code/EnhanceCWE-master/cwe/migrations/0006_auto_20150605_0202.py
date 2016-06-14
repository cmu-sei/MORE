# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cwe', '0005_auto_20150603_2250'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cwe',
            options={'default_permissions': ('add', 'change', 'delete', 'view'), 'verbose_name': 'CWE', 'verbose_name_plural': 'CWEs'},
        ),
    ]
