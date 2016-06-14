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
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from report_mailer.forms import MailerProfileForm


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
