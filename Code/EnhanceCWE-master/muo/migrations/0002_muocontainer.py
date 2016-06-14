# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cwe', '0001_initial'),
        ('muo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MUOContainer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'draft', max_length=64, editable=False, choices=[(b'draft', b'Draft'), (b'in_review', b'In Review'), (b'approved', b'Approved'), (b'rejected', b'Rejected')])),
                ('cwes', models.ManyToManyField(to='cwe.CWE')),
                ('misuse_cases', models.ManyToManyField(to='muo.MisuseCase')),
                ('osrs', models.ManyToManyField(to='muo.OSR')),
                ('use_cases', models.ManyToManyField(to='muo.UseCase')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
