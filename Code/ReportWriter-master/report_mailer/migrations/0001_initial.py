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
                ('notify_report_accepted', models.BooleanField(default=True, verbose_name=b'When My Report is Accepted')),
                ('notify_report_rejected', models.BooleanField(default=True, verbose_name=b'When My Report is Rejected')),
                ('notify_report_commented', models.BooleanField(default=True, verbose_name=b'When My Report is Commented On')),
                ('notify_report_submitted_for_review', models.BooleanField(default=True, verbose_name=b'When a Report is Submitted for Review')),
                ('notify_report_inappropriate', models.BooleanField(default=True, verbose_name=b'When a Report is Reported Inappropriate')),
                ('notify_report_saved_enhancedCWEApplication', models.BooleanField(default=True, verbose_name=b'When a Report is saved in EnhancedCWE')),
            ],
        ),
    ]
