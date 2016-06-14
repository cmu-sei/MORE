# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from base.migrations import DifferentAppMigration


class Migration(DifferentAppMigration):
    """
    Note the usage of DifferentAppMigration instead of default migration class
    """

    migrated_app = 'account'

    dependencies = [
        ('account', '0001_initial'),
        ('register_clients', '0001_initial'),
    ]

    operations = [

        migrations.AddField(
            model_name='emailaddress',
            name='requested_role',
            field=models.CharField(max_length=20, choices=[(b'contributor', b'Contributor'), (b'client', b'Client')],
                                   default=b'contributor'),
        ),
    ]
