# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('invitation', '0003_auto_20150703_0555'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailinvitation',
            name='status',
            field=models.CharField(default=b'Pending', max_length=64, choices=[(b'accepted', b'Accepted'), (b'pending', b'Pending')]),
        ),
    ]
