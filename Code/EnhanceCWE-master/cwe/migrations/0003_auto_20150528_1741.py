# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cwe', '0002_auto_20150528_1733'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='modified',
            new_name='modified_at',
        ),
        migrations.RenameField(
            model_name='cwe',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='cwe',
            old_name='modified',
            new_name='modified_at',
        ),
        migrations.RenameField(
            model_name='keyword',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='keyword',
            old_name='modified',
            new_name='modified_at',
        ),
    ]
