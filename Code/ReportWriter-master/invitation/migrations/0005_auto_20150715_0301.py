# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0004_emailinvitation_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailinvitation',
            name='email',
            field=models.EmailField(unique=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='emailinvitation',
            name='status',
            field=models.CharField(default=b'pending', max_length=64, choices=[(b'accepted', b'Accepted'), (b'pending', b'Pending')]),
        ),
    ]
