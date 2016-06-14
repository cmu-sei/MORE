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
from captcha.fields import ReCaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div
from allauth.account.forms import SignupForm, LoginForm
from allauth.account import app_settings
from allauth.account.forms import authenticate
from django.utils.translation import ugettext_lazy as _
from .settings import NUMBER_OF_FAILED_LOGINS_BEFORE_CAPTCHA

class CaptchaLoginForm(LoginForm):
    recaptcha = ReCaptchaField(label="I'm a human", required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(CaptchaLoginForm, self).__init__(*args, **kwargs)

        # Display captcha after N failed attempts
        if self.request.session.get('invalid_login_attempts', 0) >= NUMBER_OF_FAILED_LOGINS_BEFORE_CAPTCHA:
            self.fields.update({'recaptcha': self.declared_fields['recaptcha']})

    def clean(self):
        if self._errors:
            return
        user = authenticate(**self.user_credentials())
        if user:
            self.user = user
            if 'invalid_login_attempts' in self.request.session:
                del self.request.session['invalid_login_attempts']
        else:
            # keep track of invalid login attempts
            invalid_attempts = self.request.session.get('invalid_login_attempts', 0)
            invalid_attempts += 1
            self.request.session['invalid_login_attempts'] = invalid_attempts

            raise forms.ValidationError(
                self.error_messages[
                    '%s_password_mismatch'
                    % app_settings.AUTHENTICATION_METHOD])
        return self.cleaned_data




class CustomSignupForm(SignupForm):
    """
    It is a Custom Registration Form class which overrides the default registration form class.
    Its purpose is to add two new fields to the registration form
    """

    first_name = forms.CharField(label=_('First name'), max_length=30, required=True)
    last_name = forms.CharField(label=_('Last name'), max_length=30, required=True)
    recaptcha = ReCaptchaField(label="I'm a human")


    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Div(
                Field('username', placeholder=self.fields['username'].label, wrapper_class='col-sm-12'),
                css_class='col-sm-12',
            ),
            Div(
                Field('first_name', placeholder=self.fields['first_name'].label, wrapper_class="col-sm-6"),
                Field('last_name', placeholder=self.fields['last_name'].label, wrapper_class='col-sm-6'),
                css_class='col-sm-12',
            ),
            Div(
                Field('password1', placeholder=self.fields['password1'].label, wrapper_class="col-sm-6"),
                Field('password2', placeholder=self.fields['password2'].label, wrapper_class='col-sm-6'),
                css_class='col-sm-12',
            ),
            Div(
                Field('email', placeholder=self.fields['email'].label, wrapper_class='col-sm-12'),
                css_class='col-sm-12',
            ),
            Div(
                Field('recaptcha', placeholder=self.fields['recaptcha'].label, wrapper_class='col-sm-6'),
                css_class='col-sm-12',
            ),
        )

