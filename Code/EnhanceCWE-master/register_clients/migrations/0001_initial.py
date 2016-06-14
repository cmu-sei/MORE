# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


from base.migrations import DifferentAppMigration

class Migration(DifferentAppMigration):

    migrated_app = 'auth'
    dependencies = [
        ('auth', '0005_alter_user_last_login_null'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='is_auto_assign_contributors',
            field=models.BooleanField(default=False, verbose_name='Auto Assign to Contributors'),
        ),

        migrations.AddField(
            model_name='group',
            name='is_auto_assign_client',
            field=models.BooleanField(default=False, verbose_name='Auto Assign to Clients'),
        ),




    ]
