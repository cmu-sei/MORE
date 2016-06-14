# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0024_auto_20150723_0222'),
    ]

    operations = [
        migrations.AddField(
            model_name='muocontainer',
            name='is_published',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
