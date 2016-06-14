# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RESTConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255, validators=[django.core.validators.URLValidator()])),
                ('token', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'REST Configuration',
            },
        ),
    ]
