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
from django.contrib import admin
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text
from django.utils.translation import ugettext as _


class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'primary', 'verified', 'admin_approval')
    list_filter = ('primary', 'verified', 'admin_approval')
    search_fields = ['']
    fields = [('user', 'admin_approval'), 'email', ('primary', 'verified'), 'created_at', ('modified_at', 'modified_by')]
    readonly_fields = ['admin_approval', 'created_at', 'modified_by', 'modified_at']
    raw_id_fields = ('user',)

    def get_search_fields(self, request):
        base_fields = get_adapter().get_user_search_fields()
        return ['email'] + list(map(lambda a: 'user__' + a, base_fields))



    def response_change(self, request, obj, *args, **kwargs):
        '''
        Override response_change method of admin/options.py to handle the click of
        newly added buttons
        '''

        # Get the metadata about self (it tells you app and current model)
        opts = self.model._meta
        msg = None

        # Get the primary key of the model object i.e. Issue Report
        pk_value = obj._get_pk_val()

        preserved_filters = self.get_preserved_filters(request)

        redirect_url = reverse('admin:%s_%s_change' %
                                   (opts.app_label, opts.model_name),
                                   args=(pk_value,))
        redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)

        msg_dict = {'name': force_text(opts.verbose_name), 'obj': force_text(obj)}

        # Check which button is clicked, handle accordingly.
        try:
            if "_approve" in request.POST:
                obj.action_approve()
                msg = _('The %(name)s "%(obj)s" has been approved.') % msg_dict

            elif "_reject" in request.POST:
                reject_reason = request.POST.get('reject_reason_text', '')
                obj.action_reject(reject_reason)
                msg = None

        except ValueError as e:
            # In case the state of the object is not suitable for the corresponding action,
            # model will raise the value exception with the appropriate message. Catch the
            # exception and show the error message to the user
            msg = e.message
            self.message_user(request, msg, messages.ERROR)

        if msg:
            self.message_user(request, msg, messages.SUCCESS)
        return HttpResponseRedirect(redirect_url)


admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, EmailAddressAdmin)
