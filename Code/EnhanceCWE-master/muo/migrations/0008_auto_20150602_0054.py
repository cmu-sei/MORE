# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('muo', '0007_merge'),
    ]

    operations = [
        migrations.RenameField(
            model_name='muocontainer',
            old_name='modified',
            new_name='modified_at',
        ),
        migrations.RemoveField(
            model_name='muocontainer',
            name='created',
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='created_by',
            field=models.ForeignKey(related_name='+', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='modified_by',
            field=models.ForeignKey(related_name='+', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
