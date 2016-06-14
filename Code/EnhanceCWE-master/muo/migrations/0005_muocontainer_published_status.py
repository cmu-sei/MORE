# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0004_auto_20150527_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='muocontainer',
            name='published_status',
            field=models.CharField(default=b'draft', max_length=32, choices=[(b'published', b'Published'), (b'unpublished', b'Unpublished')]),
        ),
    ]
