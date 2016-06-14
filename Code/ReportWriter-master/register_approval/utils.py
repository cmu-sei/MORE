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
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from allauth.account.app_settings import EmailVerificationMethod
from .models import EmailAddress

def check_admin_approval(request, user, email_verification, *args, **kwargs):

    # Allow super users to login regardless of admin approval
    if user.is_active and user.is_superuser:
        return

    user_email = EmailAddress.objects.filter(user=user)

    has_verified_email = user_email.filter(verified=True).exists()
    if email_verification == EmailVerificationMethod.MANDATORY and not has_verified_email:
        return


    rejected_email = user_email.filter(admin_approval='rejected')
    if rejected_email.exists():
        messages.add_message(request, messages.ERROR,
                             'Sorry, your registration request has been rejected because: %s' %
                             rejected_email[0].reject_reason)
        return HttpResponseRedirect(reverse('account_login'))


    approved_email = user_email.filter(admin_approval='approved')
    if not approved_email.exists():
        messages.add_message(request, messages.WARNING,
                             'Your registration request is pending for admin approval')
        return HttpResponseRedirect(reverse('account_login'))
