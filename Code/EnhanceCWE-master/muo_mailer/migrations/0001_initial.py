# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailerProfile',
            fields=[
                ('user', models.OneToOneField(related_name='mailer_profile', primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('notify_muo_accepted', models.BooleanField(default=True, verbose_name=b'When My MUO is Accepted')),
                ('notify_muo_rejected', models.BooleanField(default=True, verbose_name=b'When My MUO is Rejected')),
                ('notify_muo_commented', models.BooleanField(default=True, verbose_name=b'When My MUO is Commented On')),
                ('notify_muo_inappropriate', models.BooleanField(default=True, verbose_name=b'When an MUO is Reported Inappropriate')),
                ('notify_muo_submitted_for_review', models.BooleanField(default=True, verbose_name=b'When an MUO is Submitted for Review')),
                ('notify_custom_muo_created', models.BooleanField(default=True, verbose_name=b'When a Custom MUO is Created')),
                ('notify_custom_muo_promoted_as_generic', models.BooleanField(default=True, verbose_name=b'When a Custom MUO is Promoted')),
            ],
        ),
    ]
