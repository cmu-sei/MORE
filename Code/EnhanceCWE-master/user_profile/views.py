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
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from muo_mailer.forms import MailerProfileForm
from rest_framework.authtoken.models import Token


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class ProfileView(UpdateView):

    template_name = 'user_profile/profile.html'
    form_class = UserForm
    mailer_form = MailerProfileForm
    success_url = reverse_lazy('user_profile')

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileView, self).dispatch(*args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        user = self.get_object()

        if 'form' not in context:
            context['form'] = self.form_class(instance=user)

        if 'mailer_form' not in context:
            context['mailer_form'] = self.mailer_form(instance=user.mailer_profile)

        if 'rest_token' not in context:
            if getattr(user, 'auth_token', False):
                context['rest_token'] = user.auth_token
        return context


    def get_object(self):
        return self.request.user


    def form_invalid(self, **kwargs):
        """ Override the default form_invalid method as the default method returns a single form in the context """
        return self.render_to_response(self.get_context_data(**kwargs))


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if '_save' in request.POST:
            # get the primary form
            user_form = self.get_form(self.get_form_class())

            # get the mailer form
            mailer_form = self.get_form(self.mailer_form)

            if user_form.is_valid() and mailer_form.is_valid():
                mailer_form.save()
                messages.add_message(request, messages.SUCCESS, "Your profile has been updated successfully")
                return self.form_valid(user_form)
            else:
                return self.form_invalid(**{'form': user_form, 'mailer_form': mailer_form})


        elif '_deactivate_account' in request.POST:
            logout(request)
            self.object.is_active = False
            self.object.save()
            messages.add_message(request, messages.WARNING, "Your account has been deactivated!")
            return HttpResponseRedirect("/")


        elif 'rest_token_submit' in request.POST:
            Token.objects.filter(user=self.object).delete()
            token = Token.objects.create(user=self.object)
            email_token_change(token)
            messages.add_message(request, messages.SUCCESS, "Your token has been updated successfully")
            return HttpResponseRedirect(self.get_success_url())



def email_token_change(token):
    sender = getattr(settings, 'SENDER_EMAIL', '')
    site_url = _current_site_url()
    profile_url = site_url + reverse('user_profile')

    send_mail(_('API Token Updated'), get_template('user_profile/email_token_change.html').render(
        Context({
            'user': token.user,
            'current_site': Site.objects.get_current(),
            'profile_url': profile_url,
        })
    ), sender, [token.user.email], fail_silently=True)


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
