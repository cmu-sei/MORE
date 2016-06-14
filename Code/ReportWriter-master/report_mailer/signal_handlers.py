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
from django.core.mail import send_mail, get_connection, EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.template import Context
from django.contrib.auth.models import User, Permission
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django_comments.signals import comment_was_posted

from report.models import *
import constants

SENDER_EMAIL = getattr(settings, 'SENDER_EMAIL', '')

"""
All of these methods are the handlers for the signals defined in signals.py in the
Report Writing Application.
They create the email body by fetching the parameters and send the email
"""

# This method will send an email when a Report gets accepted
@receiver(report_accepted)
def on_report_accepted(sender, instance, **kwargs):
    if instance.created_by and instance.created_by.mailer_profile.notify_report_accepted:
        message = "Your %s has been accepted" % instance.name
        notify_owner(instance, message)

# This method will send an email when a Report gets rejected
@receiver(report_rejected)
def on_report_rejected(sender, instance, **kwargs):
    if instance.created_by and instance.created_by.mailer_profile.notify_report_rejected:
        message = "Your %s has been rejected" % instance.name
        notify_owner(instance, message)


# This method will send an email when a Report is marked as inappropriate/duplicate
@receiver(post_save, sender=IssueReport)
def on_report_inappropriate(sender, instance, created=False, **kwargs):
    if created:
        report_type = ContentType.objects.get(app_label='report', model='report')
        # First filter the permission which has to be checked from the list of permission in the report
        perm = Permission.objects.filter(codename__in=('can_approve', 'can_reject'), content_type = report_type)
        # The user might have the permission either as a user or in a group of which he is a part, so check both
        users = User.objects.filter(mailer_profile__notify_report_inappropriate=True)\
                            .filter(Q(groups__permissions__in=perm) | Q(user_permissions__in=perm)).distinct()
        message = "%s has been marked as inappropriate" % instance.report.name
        notify_reviewers(instance.report, message, users)


# This method will send an email when the Report is submitted for review. It will notify the reviewers
@receiver(report_submitted_review)
def on_report_submitted_for_review(sender,instance, **kwargs):
    report_type = ContentType.objects.get(app_label='report', model='report')
    # First filter the permission which has to be checked from the list of permission in the report
    perm = Permission.objects.filter(codename__in=('can_approve', 'can_reject'), content_type = report_type)
    # The user might have the permission either as a user or in a group of which he is a part, so check both
    users = User.objects.filter(mailer_profile__notify_report_submitted_for_review=True)\
                        .filter(Q(groups__permissions__in=perm) | Q(user_permissions__in=perm)).distinct()
    message = "%s has been submitted for review" % instance.name
    notify_reviewers(instance, message, users)



@receiver(report_saved_enhancedCWEApplication)
def on_report_saved(sender,instance, **kwargs):
    """
    TODO Handler will be written when this user story is implemented
    """
    pass


def notify_owner(instance, message):
    thread = threading.Thread(target=_notify_owner, args=(instance, message))
    thread.start()


def _notify_owner(instance, message):
    """
    This method is called when we have to send the email after fixing all the parameters
    """
    user = instance.created_by
    body = get_template('mailer/base_site.html').render(
        Context({
            'username': user.get_full_name() or user.username,
            'body': message,
        })
    )
    send_mail(message, message, SENDER_EMAIL, [user.email], html_message=body, fail_silently=True)


def notify_reviewers(instance, message, users):
    thread = threading.Thread(target=_notify_reviewers, args=(instance, message, users))
    thread.start()


def _notify_reviewers(instance, message, users):
    """
    This method is called when we have to send bulk email to many recipients
    """
    connection = get_connection()
    connection.open()
    messages = list()

    for user in users:
        if user.email:
            context = {
                'username': user.get_full_name() or user.username,
                'body': message,
            }
            subject, from_email, to = message, SENDER_EMAIL, user.email
            text_content = message
            html_content = render_to_string('mailer/base_site.html', context)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            messages.append(msg)

    connection.send_messages(messages)
    connection.close()


