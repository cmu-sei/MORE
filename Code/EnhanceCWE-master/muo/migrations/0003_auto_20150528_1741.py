# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('muo', '0002_auto_20150528_1733'),
    ]

    operations = [
        migrations.RenameField(
            model_name='misusecase',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='misusecase',
            old_name='modified',
            new_name='modified_at',
        ),
        migrations.RenameField(
            model_name='osr',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='osr',
            old_name='modified',
            new_name='modified_at',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='modified',
            new_name='modified_at',
        ),
        migrations.RenameField(
            model_name='usecase',
            old_name='created',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='usecase',
            old_name='modified',
            new_name='modified_at',
        ),
    ]
