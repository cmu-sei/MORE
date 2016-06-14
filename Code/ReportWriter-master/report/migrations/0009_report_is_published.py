# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0008_issuereport'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='is_published',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
