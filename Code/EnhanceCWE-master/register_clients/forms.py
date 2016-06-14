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
from crispy_forms.bootstrap import InlineRadios
from django import forms
from django.contrib.auth.models import Group
from crispy_forms.layout import Div
from django.utils.translation import ugettext_lazy as _
from allauth.account.models import EmailAddress

from register.forms import CustomSignupForm


class CustomSignupFormClient(CustomSignupForm):
    """
    It is a Custom Registration Form class which adds extra fields to the default registration form.
    Here we are adding 'role' as an extra field.
    """

    role = forms.ChoiceField(label=_('Role'), choices=(('contributor', "Contributor"), ('client', "Client")),
                             widget=forms.RadioSelect(), initial='contributor')

    def __init__(self, *args, **kwargs):
        super(CustomSignupFormClient, self).__init__(*args, **kwargs)
        layout_for_radio_button = Div(
            InlineRadios('role', wrapper_class='col-sm-12'),
            css_class='col-sm-12'
        )
        self.helper.layout.insert(4, layout_for_radio_button)


    def save(self, request):
        """
        We are overriding this method to save the extra information related to the user.
        In this case, this extra information is the role requested.

        This method adds users after saving them to default groups as defined by 'is_auto_assign_contributor' and
        'is_auto_assign_client'
        """
        user = super(CustomSignupFormClient, self).save(request)

        role = request.POST.get('role')
        if role:
            email = EmailAddress.objects.filter(user=user)[0]
            email.requested_role = role
            email.save()

            # Filter all those groups with assignable attribute set to True
            if role == 'client':
                groups = list(Group.objects.filter(is_auto_assign_client=True))
                user.groups.add(*groups)

            # Filter all those groups with assignable attribute set to True
            if role == 'contributor':
                groups = list(Group.objects.filter(is_auto_assign_contributors=True))
                user.groups.add(*groups)

        return user
