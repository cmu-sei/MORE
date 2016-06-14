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
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import models
from django.template import Context
from django.template.loader import get_template
from django.utils import timezone
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from allauth.account.models import EmailAddress
from mailer.util import send_email
from .signals import register_approved, register_rejected

SENDER_EMAIL = getattr(settings, 'SENDER_EMAIL', '')
SITE_TITLE = getattr(settings, 'SITE_TITLE', '')


""" Adding additional fields to EmailAddress """
if not hasattr(EmailAddress, 'admin_approval'):
    field = models.CharField(choices=[('pending', 'Pending'),
                                               ('approved', 'Approved'),
                                               ('rejected', 'Rejected')], max_length=32, db_index=True, default='pending')
    field.contribute_to_class(EmailAddress, 'admin_approval')


if not hasattr(EmailAddress, 'reject_reason'):
    field = models.TextField(null=True, blank=True)
    field.contribute_to_class(EmailAddress, 'reject_reason')


if not hasattr(EmailAddress, 'created_at'):
    field = models.DateTimeField(default=timezone.now)
    field.contribute_to_class(EmailAddress, 'created_at')


if not hasattr(EmailAddress, 'modified_at'):
    field = models.DateTimeField(auto_now=True)
    field.contribute_to_class(EmailAddress, 'modified_at')


if not hasattr(EmailAddress, 'modified_by'):
    field = models.ForeignKey(User, null=True, related_name='+')
    field.contribute_to_class(EmailAddress, 'modified_by')


""" Adding additional methods to EmailAddress """
def action_approve(self):
    self.admin_approval = 'approved'
    self.save()
    register_approved.send(sender=self.__class__, instance=self)

if not hasattr(EmailAddress, 'action_approve'):
    EmailAddress.action_approve = action_approve


def action_reject(self, reject_reason=None):
    self.admin_approval = 'rejected'
    self.reject_reason = reject_reason
    self.save()
    # send signal
    register_rejected.send(sender=self.__class__, instance=self)


if not hasattr(EmailAddress, 'action_reject'):
    EmailAddress.action_reject = action_reject


@receiver(register_approved)
def email_on_approve(sender, instance, **kwargs):
    """ This method will send an email when registration gets approved """

    site_url = _current_site_url()
    login_url = site_url + reverse('account_login')
    message = "Your request to register at %s has been approved.\n\n" \
              "You can now log in to your account through %s" % (SITE_TITLE, login_url)

    send_email(subject=_('Registration Request Accepted'), users=[instance.user], message=message, context=Context({
        'username': instance.user.get_full_name() or instance.user.username,
        'body': message,
        'login_url': login_url,
    }))




@receiver(register_rejected)
def email_on_reject(sender, instance, **kwargs):
    """ This method will send an email when registration gets rejected """
    message = "Unfortunately, Your request to register at %s has been rejected because:\n%s" % ( SITE_TITLE, instance.reject_reason)
    send_email(subject=_('Registration Request Rejected'), users=[instance.user], message=message, context=Context({
        'username': instance.user.get_full_name() or instance.user.username,
        'body': message,
    }))





def _current_site_url():
    """Returns fully qualified URL (no trailing slash) for the current site."""
    from django.contrib.sites.models import Site

    current_site = Site.objects.get_current()
    protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
    port = getattr(settings, 'MY_SITE_PORT', '')
    url = '%s://%s' % (protocol, current_site.domain)
    if port:
        url += ':%s' % port
    return url
