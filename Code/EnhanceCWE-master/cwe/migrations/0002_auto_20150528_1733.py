# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cwe', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='created_by',
            field=models.ForeignKey(related_name='+', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='category',
            name='modified_by',
            field=models.ForeignKey(related_name='+', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cwe',
            name='created_by',
            field=models.ForeignKey(related_name='+', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='cwe',
            name='modified_by',
            field=models.ForeignKey(related_name='+', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='keyword',
            name='created_by',
            field=models.ForeignKey(related_name='+', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='keyword',
            name='modified_by',
            field=models.ForeignKey(related_name='+', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
