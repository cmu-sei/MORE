# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cwe', '0006_auto_20150605_0202'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'default_permissions': ('add', 'change', 'delete', 'view'), 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
    ]
