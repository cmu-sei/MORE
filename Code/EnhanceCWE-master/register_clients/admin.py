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
from allauth.account.models import EmailAddress
from base.admin import BaseAdmin
from register_approval.admin import EmailAddressAdmin


class ClientEmailAddressAdmin(EmailAddressAdmin):
    list_display = ('email', 'user', 'primary', 'verified', 'admin_approval', 'requested_role')
    list_filter = ('primary', 'verified', 'admin_approval', 'requested_role')

    fields = [('user', 'admin_approval'), 'email', ('primary', 'verified'), 'created_at', ('modified_at', 'modified_by'), 'requested_role']
    readonly_fields = ['admin_approval', 'created_at', 'modified_by', 'modified_at']
    raw_id_fields = ('user',)

admin.site.unregister(EmailAddress)
admin.site.register(EmailAddress, ClientEmailAddressAdmin)
