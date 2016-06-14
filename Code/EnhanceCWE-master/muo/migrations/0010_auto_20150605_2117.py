# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0009_auto_20150603_2250'),
    ]

    operations = [
        migrations.AddField(
            model_name='misusecase',
            name='name',
            field=models.CharField(default=b'/', max_length=16, null=True, db_index=True, blank=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='name',
            field=models.CharField(default=b'/', max_length=16, null=True, db_index=True, blank=True),
        ),
        migrations.AddField(
            model_name='osr',
            name='name',
            field=models.CharField(default=b'/', max_length=16, null=True, db_index=True, blank=True),
        ),
        migrations.AddField(
            model_name='usecase',
            name='name',
            field=models.CharField(default=b'/', max_length=16, null=True, db_index=True, blank=True),
        ),
    ]
