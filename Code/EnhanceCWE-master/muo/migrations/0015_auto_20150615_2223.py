# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('muo', '0014_auto_20150612_2008'),
    ]

    operations = [
        migrations.AddField(
            model_name='muocontainer',
            name='reject_reason',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='reviewed_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
