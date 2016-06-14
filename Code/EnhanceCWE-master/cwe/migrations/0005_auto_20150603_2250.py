# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cwe', '0004_auto_20150528_1751'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='active',
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name='cwe',
            name='active',
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AddField(
            model_name='keyword',
            name='active',
            field=models.BooleanField(default=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='created_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='modified_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='cwe',
            name='created_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='cwe',
            name='modified_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='keyword',
            name='created_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='keyword',
            name='modified_by',
            field=models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
