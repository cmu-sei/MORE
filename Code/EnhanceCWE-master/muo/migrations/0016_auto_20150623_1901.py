# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('muo', '0015_auto_20150615_2223'),
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
                ('status', models.CharField(default=b'new', max_length=64, choices=[(b'new', b'New'), (b'investigating', b'Investigating'), (b're-investigating', b'Re-Investigating'), (b'resolved', b'Resolved')])),
                ('created_by', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
                ('modified_by', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Issue Report',
                'verbose_name_plural': 'Issue Reports',
            },
        ),
        migrations.AlterField(
            model_name='misusecase',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='muocontainer',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='tag',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='usecase',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='issuereport',
            name='usecase',
            field=models.ForeignKey(related_name='issue_reports', to='muo.UseCase'),
        ),
        migrations.AddField(
            model_name='issuereport',
            name='usecase_duplicate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='muo.UseCase', null=True),
        ),
    ]
