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
from django.db import models
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from base.models import BaseModel
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from django.core.urlresolvers import reverse

SENDER_EMAIL = getattr(settings, 'SENDER_EMAIL', '')

STATUS = [('accepted', 'Accepted'),
          ('pending', 'Pending')]

class EmailInvitation(BaseModel):
    email = models.EmailField(max_length=256, unique=True)
    key = models.CharField(verbose_name='key', max_length=64, db_index=True)
    status = models.CharField(choices=STATUS, max_length=64, default='pending')

    def __unicode__(self):
        return "to %s" % self.email


    def send_invitation(self):
        """
        This method is used to invoke send_email() to send the invitation email to the new user after he is saved in the db
        """
        key = self.key
        email = self.email
        subject = 'Enhanced CWE Invitation'
        site_path = reverse("account_signup")
        site_url = current_site_url()

        send_mail(subject, get_template('invitation/invitation_invite_email.html').render(
            Context({
                'key': key,
                'email': email,
                'site_path': site_path,
                'site_url': site_url
            })
        ), SENDER_EMAIL, [email], fail_silently=True)


@receiver(pre_save, sender=EmailInvitation, dispatch_uid='emailinvite_pre_save_signal')
def pre_save_update_key(sender, instance, *args, **kwargs):
    """
    Since the key is generated randomly at runtime, this class method is called for attaching
    the key to the current invitation instance.
    """
    if not instance.key:
        random_key = get_random_string(64).lower()
        instance.key = random_key


def current_site_url():
    """Returns fully qualified URL (no trailing slash) for the current site."""
    from django.contrib.sites.models import Site

    current_site = Site.objects.get_current()
    protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
    port = getattr(settings, 'MY_SITE_PORT', '')
    url = '%s://%s' % (protocol, current_site.domain)
    if port:
        url += ':%s' % port
    return url
