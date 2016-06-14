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
from urlparse import urlparse, parse_qs

from django.core.urlresolvers import reverse
from allauth.account.models import EmailAddress

from invitation.models import EmailInvitation


def verify_email_if_invited(request, user, *args, **kwargs):
    """
    This method should be registered in ACCOUNT_EXTRA_PRE_LOGIN_STEPS to verify the email address of the user
    if the user came from invitation link
     """
    url = urlparse(str(request.META['HTTP_REFERER']))

    # check if coming from registration page
    if url.path == reverse('account_signup'):
        # Here I am checking if there is some token in the query string or not.
        # If there is a token then verify it and set the EmailVerificationMethod = NONE
        params = parse_qs(url.query)
        email_local = None
        token_local = None

        if 'token' in params and 'email' in params:
            email_local = params['email'][0]
            token_local = params['token'][0]
        elif 'invite_email' in request.session and 'invite_token' in request.session:
            email_local = request.session['invite_email']
            token_local = request.session['invite_token']

        if email_local and token_local:
            if EmailInvitation.objects.filter(email=email_local, key=token_local).exists():
                email_obj = EmailAddress.objects.get(user=user, email=email_local)
                email_obj.verified = True

                # if register_approval is installed, then we mark the registration as approved
                if hasattr(email_obj, 'admin_approval'):
                    email_obj.admin_approval = 'approved'

                email_obj.save()

                # change status of invitation
                invitation = EmailInvitation.objects.filter(email=email_local, key=token_local)[0]
                invitation.status = 'accepted'
                invitation.save()

            if 'invite_email' in request.session:
                del request.session['invite_email']

            if 'invite_token' in request.session:
                del request.session['invite_token']
