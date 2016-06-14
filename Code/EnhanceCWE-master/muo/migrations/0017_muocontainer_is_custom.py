# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0016_auto_20150623_1901'),
    ]

    operations = [
        migrations.AddField(
            model_name='muocontainer',
            name='is_custom',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
