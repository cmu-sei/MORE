# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0018_auto_20150628_0356'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='muocontainer',
            options={'verbose_name': 'MUO Container', 'verbose_name_plural': 'MUO Containers', 'permissions': (('can_approve', 'Can approve MUO container'), ('can_reject', 'Can reject MUO container'), ('can_view_all', 'Can view all MUO containers'))},
        ),
    ]
