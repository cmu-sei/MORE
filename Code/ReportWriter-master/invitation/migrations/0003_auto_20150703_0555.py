# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0002_auto_20150703_0513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailinvitation',
            name='key',
            field=models.CharField(max_length=64, verbose_name=b'key', db_index=True),
        ),
    ]
