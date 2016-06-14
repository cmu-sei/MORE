# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('cwe', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MisuseCase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('cwes', models.ManyToManyField(related_name='misuse_cases', to='cwe.CWE')),
            ],
            options={
                'verbose_name': 'Misuse Case',
                'verbose_name_plural': 'Misuse Cases',
            },
        ),
        migrations.CreateModel(
            name='OSR',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
            ],
            options={
                'verbose_name': 'Overlooked Security Requirement',
                'verbose_name_plural': 'Overlooked Security Requirements',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(unique=True, max_length=32)),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.CreateModel(
            name='UseCase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', models.TextField()),
                ('misuse_case', models.ForeignKey(related_name='use_cases', on_delete=b'Cascade', to='muo.MisuseCase')),
                ('tags', models.ManyToManyField(to='muo.Tag', blank=True)),
            ],
            options={
                'verbose_name': 'Use Case',
                'verbose_name_plural': 'Use Cases',
            },
        ),
        migrations.AddField(
            model_name='osr',
            name='tags',
            field=models.ManyToManyField(to='muo.Tag', blank=True),
        ),
        migrations.AddField(
            model_name='osr',
            name='use_case',
            field=models.ForeignKey(related_name='osrs', on_delete=b'Cascade', to='muo.UseCase'),
        ),
        migrations.AddField(
            model_name='misusecase',
            name='tags',
            field=models.ManyToManyField(to='muo.Tag', blank=True),
        ),
    ]
