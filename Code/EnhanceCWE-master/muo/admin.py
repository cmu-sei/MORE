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
from django.db.models import Q
from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.template.response import TemplateResponse
from django.conf.urls import url
import autocomplete_light
from models import *
from django.utils.safestring import mark_safe

from django.http import HttpResponseRedirect
from base.admin import BaseAdmin

# Tags are not used anywhere for now
# @admin.register(Tag)
# class TagAdmin(BaseAdmin):
#     fields = ['name']
#     search_fields = ['name']


@admin.register(UseCase)
class UseCaseAdmin(BaseAdmin):
    fields = ['name', 'misuse_case', 'use_case_description', 'osr', 'tags']
    readonly_fields = ['name']
    list_display = ['name']
    search_fields = ['name', 'use_case_description', 'tags__name']

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}

class UseCaseAdminInLine(admin.StackedInline):
    model = UseCase
    extra = 0
    fields = ['name', 'use_case_description', 'use_case_primary_actor',
              'use_case_secondary_actor', 'use_case_precondition', 'use_case_flow_of_events',
              'use_case_postcondition', 'use_case_assumption', 'use_case_source',
              'osr_pattern_type', 'osr']
    readonly_fields = ['name']

    def has_delete_permission(self, request, obj=None):
        """
        Overriding the method such that the delete option on the UseCaseAdminInline form on change form
        is not available for the users except the original author or users with 'can_edit_all' permission.
        The delete option is only available to the original author or users with 'can_edit_all' permission
        if the related MUOContainer is in draft or rejected state
        """

        if obj is None:
            # This is add form, let super handle this
            return super(UseCaseAdminInLine, self).has_delete_permission(request, obj=None)
        else:
            # This is change form. Only original author or users with 'can_edit_all' permission are allowed
            # to delete the UseCase from the related MUOContainer if it is in 'draft' or 'rejected' state
            if (request.user == obj.created_by or request.user.has_perm('muo.can_edit_all')) and obj.status in ('draft', 'rejected'):
                return super(UseCaseAdminInLine, self).has_delete_permission(request, obj=None)
            else:
                # Set deletion permission to False
                return False


    def get_readonly_fields(self, request, obj=None):
        """
        Overriding the method such that all the fields on the UseCaseAdminInline form on change form
        are read-only for all the users except the original author or users with 'can_edit_all' permission.
        Only the original author or users with 'can_edit_all' permission can edit the fields that too
        when the related MUOContainer is in the 'draft' state
        """

        if obj is None:
            # This is add form, let super handle this
            return super(UseCaseAdminInLine, self).get_readonly_fields(request, obj)
        else:
            # This is the change form. Only the original author or users with 'can_edit_all' permission
            # are allowed to edit the UseCase if the related MUOContainer is in the 'draft' state
            if (request.user == obj.created_by or request.user.has_perm('muo.can_edit_all')) and obj.status == 'draft':
                return super(UseCaseAdminInLine, self).get_readonly_fields(request, obj)
            else:
                # Set all the fields as read-only
                return list(set(
                    [field.name for field in self.opts.local_fields] +
                    [field.name for field in self.opts.local_many_to_many]
                ))

    def get_max_num(self, request, obj=None, **kwargs):
        """
        Overriding the method such that the 'Add another Use Case' option on the UseCaseAdminInline form
        on change form is not available for the users except the original author or users with 'can_edit_all'
        permission. The 'Add another UseCase' option is only available to the original author or users
        with 'can_edit_all' permission if the related MUOContainer is in draft state
        """

        if obj is None:
            # This is add form, let super handle this
            return super(UseCaseAdminInLine, self).get_max_num(request, obj=None, **kwargs)
        else:
            # This is change form. Only original author is allowed to add another Use Case in the
            # MUOContainer if it is in 'draft' state
            if (request.user == obj.created_by or request.user.has_perm('muo.can_edit_all')) and obj.status == 'draft':
                return super(UseCaseAdminInLine, self).get_max_num(request, obj=None, **kwargs)
            else:
                # No 'Add another Use Case' button
                return 0


# This class is to implement an ENUM for PUBLISH and UNPUBLISH. Used in response_change method.
class PublishUnpublishValues:
    UNPUBLISH, PUBLISH = range(2)


@admin.register(MUOContainer)
class MUOContainerAdmin(BaseAdmin):
    form = autocomplete_light.modelform_factory(MUOContainer, fields="__all__")
    fields = ['name', 'cwes', 'misuse_case_type', 'misuse_case', 'misuse_case_description',
              'misuse_case_primary_actor', 'misuse_case_secondary_actor', 'misuse_case_precondition',
              'misuse_case_flow_of_events', 'misuse_case_postcondition', 'misuse_case_assumption',
              'misuse_case_source', 'status']
    list_display = ['name', 'status']
    readonly_fields = ['name', 'status']
    search_fields = ['name', 'status']
    date_hierarchy = 'created_at'
    list_filter = ['status', 'is_published', ('created_by', admin.RelatedOnlyFieldListFilter)]
    inlines = [UseCaseAdminInLine]

    def get_actions(self, request):
        """
        Overriding the method in order to disable the delete selected (and bulk delete) option the
        changelist form
        """
        actions = super(MUOContainerAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        """
            If user doesn't have access to view all MUO Containers (review), then limit to his own MUOs
            or to approved MUOs written by other contributors
        """
        qs = super(MUOContainerAdmin, self).get_queryset(request)
        if request.user.has_perm('muo.can_view_all') or request.user.has_perm('muo.can_edit_all'):
            return qs
        return qs.filter(Q(created_by=request.user) | Q(status='approved'))


    def get_readonly_fields(self, request, obj=None):
        """
        Overriding the method such that the change form is read-only for all the users. Only the original
        author of the MUOContainer or the users with 'can_edit_all' permission can edit it that too only
        when MUOContainer is in 'draft' state
        """

        if obj is None:
            # This is add form, let super handle this
            return super(MUOContainerAdmin, self).get_readonly_fields(request, obj)
        else:
            # This is change form. Only original author or users with 'can_edit_all' permission are allowed
            # to edit the MUOContainer in draft state
            if (request.user == obj.created_by or request.user.has_perm('muo.can_edit_all')) and obj.status == 'draft':
                return super(MUOContainerAdmin, self).get_readonly_fields(request, obj)
            else:
                # Set all the fields as read-only
                return list(set(
                    [field.name for field in self.opts.local_fields] +
                    [field.name for field in self.opts.local_many_to_many]
                ))


    def has_delete_permission(self, request, obj=None):
        """
        Overriding the method such that the delete option on the change form is not available
        for the users except the original author or users with permission 'can_edit_all'.
        The delete option is only available to the original author or users with permission 'can_edit_all'
        if the related MUOContainer is in draft or rejected state
        """

        if obj is None:
            # This is add form, let super handle this
            return super(MUOContainerAdmin, self).has_delete_permission(request, obj=None)
        else:
            # This is change form. Only original author or users with 'can_edit_all' are allowed
            # to delete the MUOContainer and that too if it is in 'draft' state
            if (request.user == obj.created_by or request.user.has_perm('muo.can_edit_all')) and obj.status in ('draft', 'rejected'):
                return super(MUOContainerAdmin, self).has_delete_permission(request, obj=None)
            else:
                # Set deletion permission to False
                return False


    def response_change(self, request, obj, *args, **kwargs):
        '''
        Override response_change method of admin/options.py to handle the click of
        newly added buttons
        '''

        # Get the metadata about self (it tells you app and current model)
        opts = self.model._meta

        # Get the primary key of the model object i.e. MUO Container
        pk_value = obj._get_pk_val()

        preserved_filters = self.get_preserved_filters(request)

        redirect_url = reverse('admin:%s_%s_change' %
                                   (opts.app_label, opts.model_name),
                                   args=(pk_value,))
        redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)

        # Check which button is clicked, handle accordingly.
        try:
            if "_approve" in request.POST:
                obj.action_approve(request.user)
                msg = "You have approved the submission"

            elif "_reject" in request.POST:
                reject_reason = request.POST.get('reject_reason_text', '')
                obj.action_reject(reject_reason, request.user)
                msg = "The submission has been sent back to the author for review"

            elif "_submit_for_review" in request.POST:
                obj.action_submit()
                msg = "Your review request has been successfully submitted"

            elif "_edit" in request.POST:
                obj.action_save_in_draft()
                msg = "You can now edit the MUO"

            elif "_promote" in request.POST:
                obj.action_promote(request.user)
                msg = "This MUO has been promoted and now everyone will have access to it."

            elif "_unpublish" in request.POST:
                obj.action_set_publish(PublishUnpublishValues.UNPUBLISH)
                msg = "This MUO has been unpublished."

            elif "_publish" in request.POST:
                obj.action_set_publish(PublishUnpublishValues.PUBLISH)
                msg = "This MUO has been published."

            else:
                # Let super class 'ModelAdmin' handle rest of the button clicks i.e. 'save' 'save and continue' etc.
                return super(MUOContainerAdmin, self).response_change(request, obj, *args, **kwargs)
        except ValueError as e:
            # In case the state of the object is not suitable for the corresponding action,
            # model will raise the value exception with the appropriate message. Catch the
            # exception and show the error message to the user
            msg = e.message
            self.message_user(request, msg, messages.ERROR)
            return HttpResponseRedirect(redirect_url)
        except ValidationError as e:
            # If incomplete MUO Container is attempted to be approved or submitted for review, a validation error will
            # be raised with an appropriate message
            msg = e.message
            self.message_user(request, msg, messages.ERROR)
            return HttpResponseRedirect(redirect_url)

        self.message_user(request, msg, messages.SUCCESS)
        return HttpResponseRedirect(redirect_url)


@admin.register(IssueReport)
class IssueReportAdmin(BaseAdmin):
    form = autocomplete_light.modelform_factory(IssueReport, fields="__all__")
    fields = [('name', 'status'), 'type', 'usecase', 'usecase_duplicate', 'description',
              ('created_by', 'created_at'), ('reviewed_by', 'reviewed_at'), 'resolve_reason']
    readonly_fields = ['name', 'status', 'created_by', 'created_at', 'reviewed_by', 'reviewed_at', 'resolve_reason']
    list_display = ['name', 'type', 'created_by', 'created_at', 'status',]
    search_fields = ['name', 'usecase__id', 'usecase__name', 'created_by__name']
    list_filter = ['type', 'status']
    date_hierarchy = 'created_at'


    def get_fields(self, request, obj=None):
        """ Override to hide the 'usecase_duplicate' if type is not 'duplicate' """
        fields = super(IssueReportAdmin, self).get_fields(request, obj)

        if obj and obj.type != 'duplicate' and 'usecase_duplicate' in fields:
            fields.remove('usecase_duplicate')

        return fields


    def response_change(self, request, obj, *args, **kwargs):
        '''
        Override response_change method of admin/options.py to handle the click of
        newly added buttons
        '''

        # Get the metadata about self (it tells you app and current model)
        opts = self.model._meta

        # Get the primary key of the model object i.e. Issue Report
        pk_value = obj._get_pk_val()

        preserved_filters = self.get_preserved_filters(request)

        redirect_url = reverse('admin:%s_%s_change' %
                                   (opts.app_label, opts.model_name),
                                   args=(pk_value,))
        redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)

        # Check which button is clicked, handle accordingly.
        try:
            if "_investigate" in request.POST:
                obj.action_investigate(request.user)
                msg = "The issue is now being investigated."

            elif "_resolve" in request.POST:
                resolve_reason = request.POST.get('resolve_reason_text', '')
                obj.action_resolve(resolve_reason,request.user)
                msg = "The issue is now resolved because  " + resolve_reason

            elif "_reopen" in request.POST:
                obj.action_reopen(request.user)
                msg = "The issue has been re-opened."

            elif "_open" in request.POST:
                obj.action_open(request.user)
                msg = "The issue is now opened."

        except ValueError as e:
            # In case the state of the object is not suitable for the corresponding action,
            # model will raise the value exception with the appropriate message. Catch the
            # exception and show the error message to the user
            msg = e.message
            self.message_user(request, msg, messages.ERROR)

        self.message_user(request, msg, messages.SUCCESS)
        return HttpResponseRedirect(redirect_url)
