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
from django.http import Http404, JsonResponse

from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.template.response import TemplateResponse
from django.conf.urls import url
import autocomplete_light
from django.utils.safestring import mark_safe


from django.contrib import admin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters

from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.db.models import Q
from base.admin import BaseAdmin
from rest_api.utils import rest_api
from models import *
from .settings import SELECT_CWE_PAGE_LIMIT


@admin.register(CWE)
class CWEAdmin(BaseAdmin):
    model = CWE
    fields = ['code', 'name']
    search_fields = ['name', 'code']
    list_filter = [('created_by', admin.RelatedOnlyFieldListFilter)]
    date_hierarchy = 'created_at'

class ReportForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        # Make some fields not required so they can be displayed as readonly or hidden fields
        if 'cwe' in self.fields:
            self.fields['cwes'].required = False

        if 'name' in self.fields:
            self.fields['name'].widget.attrs['readonly'] = True
            self.fields['name'].widget.attrs['disabled'] = True

        if 'status' in self.fields:
            self.fields['status'].widget.attrs['readonly'] = True
            self.fields['status'].widget.attrs['disabled'] = True
            self.fields['status'].required = False


    def clean_name(self):
        """ Since name is readonly, we make it read the original instance value """
        return self.instance.name


    def clean_cwes(self):
        if not self.instance.id or self.data.get('cwe_changed') == 'true':
            selected_cwes = self.data.getlist('selected_cwes')
            cwes = self._get_selected_cwes(selected_cwes)

            if not cwes:
                raise forms.ValidationError("This field is required.")

            return cwes

        return self.cleaned_data['cwes']


    def _get_selected_cwes(self, selected_cwes):
        """
            This method handles the logic of creating and assigning suggested CWEs to the report
        """
        result = []

        if selected_cwes:

            # selected cwes are in the format code-name, so we split by first occurrence of '-' to get the code and name
            cwe_codes = []
            cwe_names = {}
            for cwe in selected_cwes:
                record = cwe.split('_', 1)
                code = int(record[0])
                name = record[1]
                cwe_codes.append(code)
                cwe_names[code] = name

            # get the list names of the already existing cwes in the database
            existing_cwes = CWE.objects.values('code')
            existing_cwes = [cwe['code'] for cwe in existing_cwes]

            # cwes that do not exist in the database
            to_add_db = [code for code in cwe_codes if code not in existing_cwes]

            # Note that using bulk_create() is very efficient as it only requires a single database query,
            # but it will not call save(), pre_save() or post_save() on the object
            to_add_db_objs = []
            for code in to_add_db:
                to_add_db_objs.append(CWE(code=code, name=cwe_names[code]))
            CWE.objects.bulk_create(to_add_db_objs)

            result = CWE.objects.filter(code__in=cwe_codes)

        return result


@admin.register(Report)
class ReportAdmin(BaseAdmin):
    form = ReportForm
    exclude = ['created_by', 'created_at', 'modified_by', 'modified_at']
    search_fields = ['title', 'status', 'custom']
    list_display = ['name', 'created_by', 'status']
    raw_id_fields = ['cwes']


    def get_actions(self, request):
        """
        Overriding the method in order to disable the delete selected (and bulk delete) option the
        changelist form
        """
        actions = super(ReportAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


    def is_readonly(self, request, obj):
        '''
        returns a boolean value indicating whether change form should be readonly or not. Change form is always readonly
        except when it is in draft state and the current user is the author of the report or the user has the
        'can_edit_all' permission
        '''
        user = request.user
        return obj and (obj.status != 'draft' or user != obj.created_by or not user.has_perm('report.can_edit_all'))


    def get_queryset(self, request):
        """
            If user doesn't have access to view all Reports (review), then limit to his own Reports
            or to approved Reports written by other contributors
        """
        qs = super(ReportAdmin, self).get_queryset(request)
        if request.user.has_perm('report.can_view_all') or request.user.has_perm('report.can_edit_all'):
            return qs
        return qs.filter(Q(created_by=request.user) | Q(status='approved'))


    def get_readonly_fields(self, request, obj=None):
        """
        Because we can't add fields to readonly_fields array because they won't be sent to the form object otherwise,
        then we have to exclude the fields that are readonly when the form is submitted, validated and saved.
        Therefore, we check if the method is POST and return the list of fields that are supposed to be readonly to be excluded
        """
        readonly_fields = list(self.readonly_fields)

        if request.method == "POST":
            if self.is_readonly(request, obj):
                readonly_fields.extend([field.name for field in self.opts.local_fields])
                readonly_fields.extend([field.name for field in self.opts.local_many_to_many])
                readonly_fields = list(set(readonly_fields))
        return readonly_fields


    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        # Override changeform_view to decide if the if the form should be read only or not. Also pass the read only
        # variable in the context

        extra_context = extra_context or {}
        extra_context['cwe_limit'] = int(SELECT_CWE_PAGE_LIMIT)

        if object_id is not None:
            # Change form. Check if the change form should be editable or readonly

            # Get the current model instance
            current_model_instance = Report.objects.get(pk=object_id)


            extra_context['readonly'] = self.is_readonly(request, current_model_instance)

        return super(ReportAdmin, self).changeform_view(request, object_id, form_url, extra_context)


    def get_urls(self):
        urls = super(ReportAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name

        additional_urls = [
            url(r'report_init_cwes/$', self.admin_site.admin_view(self.init_cwes_view), name='%s_%s_init_cwes' % info),
            url(r'report_get_cwes/$', self.admin_site.admin_view(self.get_cwes_view), name='%s_%s_get_cwes' % info),
            url(r'report_suggest_cwes/$', self.admin_site.admin_view(self.suggest_cwes_view), name='%s_%s_suggest_cwes' % info),
            url(r'report_report_misusecases/$', self.admin_site.admin_view(self.misusecases_view)),
            url(r'report_report_usecases/$', self.admin_site.admin_view(self.usecases_view)),
        ]

        return additional_urls + urls


    def init_cwes_view(self, request):
        if not request.is_ajax():
            raise Http404()

        report_id = request.GET.get('report_id')

        if report_id and report_id != 'None':
            report = Report.objects.get(pk=report_id)
            cwes = report.cwes.all()

            if cwes:
                results = [{'id': '%s_%s' % (c.code, c.name),
                            'text': 'CWE-%s: %s' % (c.code, c.name)} for c in cwes]
                return JsonResponse({'items': results})
        else:
            return JsonResponse({'items': None})


    def get_cwes_view(self, request):
        if not request.is_ajax():
            raise Http404()

        limit = SELECT_CWE_PAGE_LIMIT
        offset = int(request.GET.get('page', 1)) - 1
        cwes = rest_api.get_cwes_with_search_string(search_string=request.GET.get('q', None),
                                                    offset=offset * limit,
                                                    limit=limit)

        if cwes['success']:
            results = [{'id': '%s_%s' % (c['code'], c['name']),
                        'text': 'CWE-%s: %s' % (c['code'], c['name'])} for c in cwes['obj']['cwe_objects']] # TODO: ask robin to change this
            return JsonResponse({'items': results, 'total_count': cwes['obj']['total_count']}) # TODO: replace total_count
        else:
            return JsonResponse({'err': cwes['msg']})


    def suggest_cwes_view(self, request):
        if not request.is_ajax():
            raise Http404()

        description = request.GET.get('description')

        if not description:
            return JsonResponse({'err': 'Description is empty!'})

        cwes = rest_api.get_cwes_for_description(description)

        if cwes['success']:
            results = [{'id': '%s_%s' % (c['code'], c['name']),
                        'text': 'CWE-%s: %s' % (c['code'], c['name'])} for c in cwes['obj']]
            return JsonResponse({'items': results})
        else:
            return JsonResponse({'err': cwes['msg']})


    def misusecases_view(self, request):
        if request.method != 'POST':
            raise Http404("Invalid access using GET request!")

        # Get the selected CWE codes string
        cwes = request.POST['cwe_codes']

        # Make a REST call to get the misuse cases related to the selected CWEs
        misuse_cases = rest_api.get_misuse_cases(cwes)

        if misuse_cases['success'] is False:
            # There was some error and the REST call was not successful
            raise Http404(misuse_cases['msg'])

        # Set the context
        context = {'misuse_cases': misuse_cases['obj']}

        return TemplateResponse(request, "admin/report/report/misusecase.html", context)


    def usecases_view(self, request):
        if request.method != 'POST':
            raise Http404("Invalid access using GET request!")

        # Get the selected misuse case id
        selected_misuse_case_id = request.POST['misuse_case_id']

        # Make a REST call to get the use cases related to the selected misuse case
        use_cases = rest_api.get_use_cases(selected_misuse_case_id)

        if use_cases['success'] is False:
            # There was some error and the REST call was not successful
            raise Http404(use_cases['msg'])

        context = {'use_cases': use_cases['obj']}

        return TemplateResponse(request, "admin/report/report/usecase.html", context)


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
                msg = "You can now edit the Report"

            elif "_unpublish" in request.POST:
                obj.action_set_publish(0)
                msg = "This MUO has been unpublished."

            elif "_publish" in request.POST:
                obj.action_set_publish(1)
                msg = "This MUO has been published."

            elif "_promote" in request.POST:
                # action_promote method is invoked on click of promote button
                muo_saved =obj.action_promote()
                msg = muo_saved['msg']


            else:
                # Let super class 'ModelAdmin' handle rest of the button clicks i.e. 'save' 'save and continue' etc.
                return super(ReportAdmin, self).response_change(request, obj, *args, **kwargs)
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
    fields = [('name', 'status'), 'type', 'report', 'report_duplicate', 'description',
              ('created_by', 'created_at'), ('reviewed_by', 'reviewed_at'), 'resolve_reason']
    readonly_fields = ['name', 'status', 'created_by', 'created_at', 'reviewed_by', 'reviewed_at', 'resolve_reason']
    list_display = ['name', 'type', 'created_by', 'created_at', 'status',]
    search_fields = ['name', 'created_by__name']
    list_filter = ['type', 'status']
    date_hierarchy = 'created_at'


    def get_fields(self, request, obj=None):
        """ Override to hide the 'usecase_duplicate' if type is not 'duplicate' """
        fields = super(IssueReportAdmin, self).get_fields(request, obj)

        if obj and obj.type != 'duplicate' and 'report_duplicate' in fields:
            fields.remove('report_duplicate')

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
