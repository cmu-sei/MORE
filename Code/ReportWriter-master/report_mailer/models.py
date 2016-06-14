# @OPENSOURCE_HEADER_START@
# MORE Tool 
# Copyright 2016 Carnegie Mellon University.
# All Rights Reserved.
#
# THIS SOFTWARE IS PROVIDED "AS IS," WITH NO WARRANTIES WHATSOEVER.
# CARNEGIE MELLON UNIVERSITY EXPRESSLY DISCLAIMS TO THE FULLEST EXTENT
# PERMITTEDBY LAW ALL EXPRESS, IMPLIED, AND STATUTORY WARRANTIES,
# INCLUDING, WITHOUT LIMITATION, THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF PROPRIETARY
# RIGHTS.
#
# Released under a modified BSD license, please see license.txt for full
# terms. DM-0003473
# @OPENSOURCE_HEADER_END@
from django.conf import settings
from django.contrib.auth.models import  User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


class MailerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True, related_name="mailer_profile")
    notify_report_accepted = models.BooleanField(default=True, verbose_name='When My Report is Accepted')
    notify_report_rejected = models.BooleanField(default=True, verbose_name='When My Report is Rejected')
    notify_report_commented = models.BooleanField(default=True, verbose_name='When My Report is Commented On')
    notify_report_submitted_for_review = models.BooleanField(default=True, verbose_name='When a Report is Submitted for Review')
    notify_report_inappropriate = models.BooleanField(default=True, verbose_name='When a Report is Reported Inappropriate')
    notify_report_saved_enhancedCWEApplication = models.BooleanField(default=True, verbose_name='When a Report is saved in EnhancedCWE')

    def __unicode__(self):
        return self.user.username

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_profile_for_user(sender, instance=None, created=False, **kwargs):
        if created:
            MailerProfile.objects.get_or_create(user=instance)

    @receiver(pre_delete, sender=settings.AUTH_USER_MODEL)
    def delete_profile_for_user(sender, instance=None, **kwargs):
        if instance:
            user_profile = MailerProfile.objects.get(user=instance)
            user_profile.delete()

User.mailer_profile = property(lambda u: MailerProfile.objects.get_or_create(user=u)[0])



