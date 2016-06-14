# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations
from base.migrations import DifferentAppMigration


class Migration(DifferentAppMigration):
    """
    Note the usage of DifferentAppMigration instead of default migration class
    """

    migrated_app = 'auth'

    dependencies = [
        ('auth', '0005_alter_user_last_login_null'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='is_auto_assign',
            field=models.BooleanField(default=False, verbose_name='Auto Assign'),
        ),

        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='email address'),
        ),

    ]