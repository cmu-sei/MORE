# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invitation', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='emailinvitation',
            name='email_address',
        ),
        migrations.AddField(
            model_name='emailinvitation',
            name='active',
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name='emailinvitation',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='emailinvitation',
            name='created_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='emailinvitation',
            name='email',
            field=models.EmailField(default='default_email', max_length=100, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailinvitation',
            name='key',
            field=models.CharField(default='default_key', unique=True, max_length=64, verbose_name=b'key', db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailinvitation',
            name='modified_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 3, 5, 13, 14, 685, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emailinvitation',
            name='modified_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
