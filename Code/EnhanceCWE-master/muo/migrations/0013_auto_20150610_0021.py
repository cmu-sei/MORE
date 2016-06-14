# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0012_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'default_permissions': ('add', 'change', 'delete', 'view'), 'verbose_name': 'Tag', 'verbose_name_plural': 'Tags'},
        ),
    ]
