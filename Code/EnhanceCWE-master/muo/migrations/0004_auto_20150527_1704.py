# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0003_auto_20150527_1632'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='muocontainer',
            options={'verbose_name': 'MUO Container', 'verbose_name_plural': 'MUO Containers'},
        ),
    ]
