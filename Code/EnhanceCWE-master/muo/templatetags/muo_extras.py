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
'''
This file will contain all the custom template tags for the
MUO app.
'''

from django.contrib.admin.templatetags.admin_modify import *
from base.templatetags.admin_modify import submit_row as original_submit_row
from django import template


register = template.Library()


@register.inclusion_tag('admin/muo/muocontainer/muo_submit_line.html', takes_context=True)
def muo_submit_row(context):
    ctx = original_submit_row(context)

    model_object = ctx.get('original')  # For add form model_object will be None
    user_object = context.get('user')

    # Get the default status of the buttons
    show_save_and_continue = ctx.get('show_save_and_continue')
    show_save_as_new = ctx.get('show_save_as_new')
    show_save = ctx.get('show_save')
    show_delete_link = ctx.get('show_delete_link')

    ctx.update({
        # Do not show save and add another button
        'show_save_and_add_another': False,

        # Always show save and delete buttons on the add form if the default status of the buttons say so
        # Show save and delete buttons on the change form only if the muo is created by the current user
        # and it is in 'draft' state and the default status is also True
        'show_save_and_continue': show_save_and_continue and
                                  (model_object is None or
                                  (model_object and
                                  model_object.status == 'draft' and
                                  (user_object == model_object.created_by or user_object.has_perm('muo.can_edit_all')))),
        'show_save_as_new': show_save_as_new and
                            (model_object is None or
                            (model_object and
                            model_object.status == 'draft' and
                            (user_object == model_object.created_by or user_object.has_perm('muo.can_edit_all')))),
        'show_save': show_save and
                     (model_object is None or
                     (model_object and
                     model_object.status == 'draft' and
                     (user_object == model_object.created_by or user_object.has_perm('muo.can_edit_all')))),
        'show_delete_link': show_delete_link and
                            (model_object is None or
                            (model_object and
                            model_object.status in ('draft', 'rejected') and
                            (user_object == model_object.created_by or user_object.has_perm('muo.can_edit_all')))),

        # Show submit for review button only to the creator of the muo and if its in draft state
        'show_submit_for_review': model_object and
                                  model_object.status == 'draft' and
                                  (user_object == model_object.created_by or user_object.has_perm('muo.can_edit_all')),

        # Show edit button only to the creator of the muo and if its either in in_review or rejected state
        'show_edit': model_object and
                     model_object.status in ('in_review', 'rejected') and
                     (user_object == model_object.created_by or user_object.has_perm('muo.can_edit_all')),

        # Show approve button only to the user if he/she has the can_approve permission and the state of
        # muo is in in_review
        'show_approve': model_object and
                        model_object.status == 'in_review' and
                        user_object.has_perm('muo.can_approve'),

        # Show reject button only to the user if he/she has the can_reject permission and the state of the
        # muo is in in_review or approved state
        'show_reject': model_object and
                       model_object.status in ('in_review', 'approved') and
                       user_object.has_perm('muo.can_reject'),

        # Show promote button only to the user if he/she has can_approve permission and the muo is custom
        # muo and its in draft state
        'show_promote': model_object and
                        model_object.is_custom == True and
                        model_object.status == 'draft' and
                        user_object.has_perm('muo.can_approve'),

        'show_publish': model_object and
                        model_object.status in ('approved',) and
                        model_object.is_published == False and
                        (user_object.has_perm('muo.can_edit_all') or user_object.has_perm('muo.can_approve') or user_object.has_perm('muo.can_reject')),

        'show_unpublish':   model_object and
                            model_object.is_published == True and
                            model_object.status in ('approved',) and
                            (user_object.has_perm('muo.can_edit_all') or user_object.has_perm('muo.can_approve') or user_object.has_perm('muo.can_reject')),
    })

    return ctx

@register.inclusion_tag('admin/muo/issuereport/reportissue_submit_line.html', takes_context=True)
def reportaction_submit_row(context):
    ctx = original_submit_row(context)

    model_object = ctx.get('original')
    user_object = context.get('user')
    ctx.update({
        # Show investigate button only when the issue is in open state and the user has approve & reject perm
        'show_investigate_issue': model_object and
                                  model_object.status in ('open','reopened') and
                                  user_object.has_perm('muo.can_approve', 'muo.can_reject'),

        # Show resolve button only when the issue is in open state and the user has approve & reject perm
        'show_resolve_issue': model_object and
                              model_object.status == 'investigating' and
                              user_object.has_perm('muo.can_approve', 'muo.can_reject'),
        'show_reopen_issue': model_object and
                             model_object.status == 'resolved' and
                             user_object.has_perm('muo.can_approve', 'muo.can_reject'),
        'show_open_issue': model_object and
                           model_object.status == 'investigating' and
                           user_object.has_perm('muo.can_approve','muo.can_reject'),

    })

    return ctx
