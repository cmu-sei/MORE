# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('report', '0007_auto_20150717_0615'),
    ]

    operations = [
        migrations.CreateModel(
            name='IssueReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(default=b'/', max_length=16, null=True, db_index=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('type', models.CharField(max_length=64, choices=[(b'incorrect', b'Incorrect Content'), (b'spam', b'Spam'), (b'duplicate', b'Duplicate')])),
                ('status', models.CharField(default=b'open', max_length=64, db_index=True, choices=[(b'open', b'Open'), (b'investigating', b'Investigating'), (b'reopened', b'Re-opened'), (b'resolved', b'Resolved')])),
                ('reviewed_at', models.DateTimeField(null=True)),
                ('resolve_reason', models.TextField(default=b'/', null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('report', models.ForeignKey(related_name='issue_reports', to='report.Report')),
                ('report_duplicate', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='report.Report', null=True)),
                ('reviewed_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Issue Report',
                'verbose_name_plural': 'Issue Reports',
            },
        ),
    ]
