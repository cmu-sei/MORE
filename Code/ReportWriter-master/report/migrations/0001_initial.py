# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CWE',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('code', models.IntegerField(unique=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(null=True, blank=True)),
                ('created_by', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'CWE',
                'verbose_name_plural': 'CWEs',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True, db_index=True)),
                ('name', models.CharField(default=b'/', max_length=16, null=True, db_index=True, blank=True)),
                ('title', models.CharField(max_length=128, db_index=True)),
                ('description', models.TextField()),
                ('misuse_case_id', models.IntegerField(null=True, blank=True)),
                ('misuse_case_description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('misuse_case_primary_actor', models.CharField(max_length=256, null=True, verbose_name=b'Primary actor', blank=True)),
                ('misuse_case_secondary_actor', models.CharField(max_length=256, null=True, verbose_name=b'Secondary actor', blank=True)),
                ('misuse_case_precondition', models.TextField(null=True, verbose_name=b'Pre-condition', blank=True)),
                ('misuse_case_flow_of_events', models.TextField(null=True, verbose_name=b'Flow of events', blank=True)),
                ('misuse_case_postcondition', models.TextField(null=True, verbose_name=b'Post-condition', blank=True)),
                ('misuse_case_assumption', models.TextField(null=True, verbose_name=b'Assumption', blank=True)),
                ('misuse_case_source', models.TextField(null=True, verbose_name=b'Source', blank=True)),
                ('use_case_id', models.IntegerField(null=True, blank=True)),
                ('use_case_description', models.TextField(null=True, verbose_name=b'Description', blank=True)),
                ('use_case_primary_actor', models.CharField(max_length=256, null=True, verbose_name=b'Primary actor', blank=True)),
                ('use_case_secondary_actor', models.CharField(max_length=256, null=True, verbose_name=b'Secondary actor', blank=True)),
                ('use_case_precondition', models.TextField(null=True, verbose_name=b'Pre-condition', blank=True)),
                ('use_case_flow_of_events', models.TextField(null=True, verbose_name=b'Flow of events', blank=True)),
                ('use_case_postcondition', models.TextField(null=True, verbose_name=b'Post-condition', blank=True)),
                ('use_case_assumption', models.TextField(null=True, verbose_name=b'Assumption', blank=True)),
                ('use_case_source', models.TextField(null=True, verbose_name=b'Source', blank=True)),
                ('osr', models.TextField(null=True, verbose_name=b'Overlooked Security Requirement', blank=True)),
                ('status', models.CharField(default=b'draft', max_length=64, choices=[(b'draft', b'Draft'), (b'in_review', b'In Review'), (b'approved', b'Approved'), (b'rejected', b'Rejected')])),
                ('promoted', models.BooleanField(default=False, db_index=True, verbose_name=b'MUO is promoted to Enhanced CWE System')),
                ('created_by', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('cwes', models.ManyToManyField(to='report.CWE', blank=True)),
                ('modified_by', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
                'permissions': (('can_approve', 'Can approve Report'), ('can_reject', 'Can reject Report'), ('can_edit_all', 'Can edit all Report'), ('can_view_all', 'Can view all Report')),
            },
        ),
    ]
