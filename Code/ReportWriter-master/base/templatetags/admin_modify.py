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
from django import template
from django.contrib.admin.templatetags.admin_modify import prepopulated_fields_js as original_prepopulated_fields_js
from django.contrib.admin.templatetags.admin_modify import cell_count as original_cell_count

register = template.Library()

@register.inclusion_tag('admin/prepopulated_fields_js.html', takes_context=True)
def prepopulated_fields_js(context):
    """ call original method so we don't break templates that call admin_modify.prepopulated_fields_js()"""
    return original_prepopulated_fields_js(context)


@register.filter
def cell_count(inline_admin_form):
    """ call original method so we don't break templates that call admin_modify.cell_count()"""
    return original_cell_count(inline_admin_form)


@register.inclusion_tag('admin/submit_line.html', takes_context=True)
def submit_row(context):
    """
    Displays the row of buttons for delete and save.
    Overridden to prevent showing save buttons if the user only has view permissions
    """
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    ctx = {
        'opts': opts,
        'show_delete_link': (
            not is_popup and context['has_delete_permission'] and
            change and context.get('show_delete', True)
        ),
        'show_save_as_new': context['add'] and context['has_add_permission']
                            and not is_popup and change and save_as, # added context['has_add_permission']
        'show_save_and_add_another': (
            context['add'] and context['has_add_permission'] and not is_popup and
            (not save_as or context['add'])
        ),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': context['has_change_permission'], # replaced True with context['has_change_permission']
        'preserved_filters': context.get('preserved_filters'),
    }
    if context.get('original') is not None:
        ctx['original'] = context['original']
    return ctx
