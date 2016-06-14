# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone
from django.conf import settings
from base.migrations import DifferentAppMigration


class Migration(DifferentAppMigration):

    migrated_app = 'account'

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0002_email_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailaddress',
            name='admin_approval',
            field=models.CharField(default=b'pending', max_length=32, db_index=True, choices=[(b'pending', b'Pending'), (b'approved', b'Approved'), (b'rejected', b'Rejected')]),
        ),
        migrations.AddField(
            model_name='emailaddress',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='emailaddress',
            name='modified_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 8, 6, 40, 18, 351467, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailaddress',
            name='modified_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='emailaddress',
            name='reject_reason',
            field=models.TextField(null=True, blank=True),
        ),
    ]
