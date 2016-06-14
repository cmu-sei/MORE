# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0023_auto_20150703_1920'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='misusecase',
            name='description',
        ),
        migrations.RemoveField(
            model_name='muocontainer',
            name='new_misuse_case',
        ),
        migrations.RemoveField(
            model_name='usecase',
            name='description',
        ),
        migrations.AddField(
            model_name='misusecase',
            name='misuse_case_assumption',
            field=models.TextField(null=True, verbose_name=b'Assumption', blank=True),
        ),
        migrations.AddField(
            model_name='misusecase',
            name='misuse_case_description',
            field=models.TextField(null=True, verbose_name=b'Brief Description', blank=True),
        ),
        migrations.AddField(
            model_name='misusecase',
            name='misuse_case_flow_of_events',
            field=models.TextField(null=True, verbose_name=b'Flow of events', blank=True),
        ),
        migrations.AddField(
            model_name='misusecase',
            name='misuse_case_postcondition',
            field=models.TextField(null=True, verbose_name=b'Post-condition', blank=True),
        ),
        migrations.AddField(
            model_name='misusecase',
            name='misuse_case_precondition',
            field=models.TextField(null=True, verbose_name=b'Pre-condition', blank=True),
        ),
        migrations.AddField(
            model_name='misusecase',
            name='misuse_case_primary_actor',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Primary actor', blank=True),
        ),
        migrations.AddField(
            model_name='misusecase',
            name='misuse_case_secondary_actor',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Secondary actor', blank=True),
        ),
        migrations.AddField(
            model_name='misusecase',
            name='misuse_case_source',
            field=models.TextField(null=True, verbose_name=b'Source', blank=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='misuse_case_assumption',
            field=models.TextField(null=True, verbose_name=b'Assumption', blank=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='misuse_case_description',
            field=models.TextField(null=True, verbose_name=b'Brief Description', blank=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='misuse_case_flow_of_events',
            field=models.TextField(null=True, verbose_name=b'Flow of events', blank=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='misuse_case_name',
            field=models.CharField(default=b'/', max_length=16, null=True, db_index=True, blank=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='misuse_case_postcondition',
            field=models.TextField(null=True, verbose_name=b'Post-condition', blank=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='misuse_case_precondition',
            field=models.TextField(null=True, verbose_name=b'Pre-condition', blank=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='misuse_case_primary_actor',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Primary actor', blank=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='misuse_case_secondary_actor',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Secondary actor', blank=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='misuse_case_source',
            field=models.TextField(null=True, verbose_name=b'Source', blank=True),
        ),
        migrations.AddField(
            model_name='muocontainer',
            name='misuse_case_type',
            field=models.CharField(default=b'new', max_length=16, null=True, verbose_name=b'Misuse Case Type', choices=[(b'existing', b'Existing'), (b'new', b'New')]),
        ),
        migrations.AddField(
            model_name='usecase',
            name='osr_pattern_type',
            field=models.CharField(default=b'ubiquitous', max_length=32, null=True, verbose_name=b'Overlooked security requirements pattern type', choices=[(b'ubiquitous', b'Ubiquitous'), (b'event-driven', b'Event-Driven'), (b'unwanted behavior', b'Unwanted Behavior'), (b'state-driven', b'State-Driven')]),
        ),
        migrations.AddField(
            model_name='usecase',
            name='use_case_assumption',
            field=models.TextField(null=True, verbose_name=b'Assumption', blank=True),
        ),
        migrations.AddField(
            model_name='usecase',
            name='use_case_description',
            field=models.TextField(null=True, verbose_name=b'Brief description', blank=True),
        ),
        migrations.AddField(
            model_name='usecase',
            name='use_case_flow_of_events',
            field=models.TextField(null=True, verbose_name=b'Flow of events', blank=True),
        ),
        migrations.AddField(
            model_name='usecase',
            name='use_case_postcondition',
            field=models.TextField(null=True, verbose_name=b'Post-condition', blank=True),
        ),
        migrations.AddField(
            model_name='usecase',
            name='use_case_precondition',
            field=models.TextField(null=True, verbose_name=b'Pre-condition', blank=True),
        ),
        migrations.AddField(
            model_name='usecase',
            name='use_case_primary_actor',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Primary actor', blank=True),
        ),
        migrations.AddField(
            model_name='usecase',
            name='use_case_secondary_actor',
            field=models.CharField(max_length=256, null=True, verbose_name=b'Secondary actor', blank=True),
        ),
        migrations.AddField(
            model_name='usecase',
            name='use_case_source',
            field=models.TextField(null=True, verbose_name=b'Source', blank=True),
        ),
        migrations.AlterField(
            model_name='usecase',
            name='osr',
            field=models.TextField(null=True, verbose_name=b'Overlooked security requirements', blank=True),
        ),
    ]
