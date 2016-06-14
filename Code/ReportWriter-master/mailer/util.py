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
import threading
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template.loader import render_to_string

SENDER_EMAIL = getattr(settings, 'SENDER_EMAIL', '')


def send_email(subject, users, message=None, template=None, context=None, fail_silently=True, **kwargs):

    if fail_silently:
        thread = threading.Thread(target=_send_email, kwargs=locals())
        thread.start()
    else:
        _send_email(**locals())



def _send_email(subject, users, message=None, template=None, context=None, fail_silently=True, **kwargs):
    connection = get_connection(fail_silently=fail_silently)
    connection.open()
    messages = list()

    for user in users:
        if user.email:
            msg = EmailMultiAlternatives(subject, message, SENDER_EMAIL, [user.email])

            if context:
                if not template:
                    template = 'mailer/base_site.html'
                context.update({'user': user,
                                'current_site': kwargs["site"] if "site" in kwargs else Site.objects.get_current(),})
                html_content = render_to_string(template, context)
                msg.attach_alternative(html_content, "text/html")

            messages.append(msg)

    connection.send_messages(messages)
    connection.close()


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
