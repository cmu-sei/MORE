# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='custom',
            field=models.BooleanField(default=False, verbose_name=b'Author has written a custom MUO'),
        ),
    ]
