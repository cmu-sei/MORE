# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0002_muocontainer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='muocontainer',
            name='status',
            field=models.CharField(default=b'draft', max_length=64, choices=[(b'draft', b'Draft'), (b'in_review', b'In Review'), (b'approved', b'Approved'), (b'rejected', b'Rejected')]),
        ),
    ]
