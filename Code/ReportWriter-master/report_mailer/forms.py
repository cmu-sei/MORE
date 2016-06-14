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
from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div

from .models import MailerProfile


class MailerProfileForm(forms.ModelForm):

    class Meta:
        model = MailerProfile
        exclude = ['user']

    def __init__(self, *args, **kwargs):

        if isinstance(kwargs.get('instance'), User):
            kwargs['instance'] = kwargs.get('instance').mailer_profile

        super(MailerProfileForm, self).__init__(*args, **kwargs)

        user = kwargs['instance'].user
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Div(
                'notify_report_accepted',
                'notify_report_rejected',
                'notify_report_commented',
                css_class='col-sm-6',
            ),
        )

        if user.has_perm('muo.can_approve') or user.has_perm('muo.can_reject'):
            self.helper.layout.append(
                Div(
                    'notify_report_submitted_for_review',
                    'notify_report_inappropriate',
                    'notify_report_saved_enhancedCWEApplication',
                    css_class='col-sm-6',
                ),
            )
