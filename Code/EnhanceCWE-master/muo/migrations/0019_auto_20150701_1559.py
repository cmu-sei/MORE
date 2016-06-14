# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0018_auto_20150628_0356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='muocontainer',
            name='misuse_case',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='muo.MisuseCase', null=True),
        ),
    ]
