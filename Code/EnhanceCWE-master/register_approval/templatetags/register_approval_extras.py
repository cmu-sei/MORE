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
from django.contrib.admin.templatetags.admin_modify import *
from django.contrib.admin.templatetags.admin_modify import submit_row as original_submit_row
from django import template


register = template.Library()


@register.inclusion_tag('admin/account/emailaddress/emailaddress_submit_line.html', takes_context=True)
def emailaddress_submit_row(context):
    ctx = original_submit_row(context)

    model_object = ctx.get('original')  # For add form model_object will be None

    ctx.update({
        # Do not show save and add another button
        'show_save_and_add_another': False,
        'show_save_as_new': False,

        'show_reject': model_object and model_object.admin_approval != 'rejected',
        'show_approve': model_object and model_object.admin_approval != 'approved',
    })

    return ctx
