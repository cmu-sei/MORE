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
import autocomplete_light
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from cwe.models import CWE
from muo.models import MisuseCase, UseCase, IssueReport
from .settings import SELECT_CWE_PAGE_LIMIT


# Home screen
def index(request):
    context = {'cwe_limit': SELECT_CWE_PAGE_LIMIT}
    return render(request, 'frontpage/index.html', context)



def get_cwes(request):
    """
    This view is called by muo search using ajax to get the list of CWEs for a given search query
    """
    if not request.is_ajax():
        return HttpResponseForbidden()

    query = request.GET.get('q')
    limit = SELECT_CWE_PAGE_LIMIT
    offset = (int(request.GET.get('page', 1)) - 1) * limit

    if query:
        if query.isdigit():
            cwes = CWE.objects.filter(Q(code__exact=query) | Q(name__icontains=query))
        else:
            cwes = CWE.objects.filter(name__icontains=query)
    else:
        cwes = CWE.objects.all()

    cwe_count = cwes.count()
    cwes = cwes[offset : offset + limit]
    results = [{'id': c.id,
                'text': 'CWE-%s: %s' % (c.code, c.name)} for c in cwes]
    return JsonResponse({'items': results, 'total_count': cwe_count})



def get_misusecases(request):
    """
    This view is called by muo search using ajax to display the misuse cases for given CWEs
    """
    if not request.is_ajax():
        raise HttpResponseForbidden()

    #  Get the selected CWE ids from the request
    selected_cwe_ids = request.POST.getlist('cwe_ids', None)
    search_term = request.POST.get('search_term', None)

    if len(selected_cwe_ids) == 0:
        # If list of CWE ids is empty return all the misuse cases
        misuse_cases = MisuseCase.objects.approved()
    else:
        #  Get the use cases for the selected CWE ids
        misuse_cases = MisuseCase.objects.filter(cwes__in=selected_cwe_ids).approved()

    if search_term:
        misuse_cases = misuse_cases.filter(Q(name__icontains=search_term) | Q(misuse_case_description__icontains=search_term))

    #  Create a context with all the corresponding misuse cases
    context = {'misuse_cases': misuse_cases,
               'search_term': search_term}

    return TemplateResponse(request, "frontpage/misusecase.html", context)


def get_usecases(request):
    """
    This view is called by muo search using ajax to display the use cases for a given misusecase
    """
    if not request.is_ajax():
        raise HttpResponseForbidden()

    misuse_case_id = request.POST['misuse_case_id']
    misuse_case = get_object_or_404(MisuseCase, pk=misuse_case_id)

    #  Create a context with all the corresponding use cases
    context = {'use_cases': misuse_case.usecase_set.approved()}

    return TemplateResponse(request, "frontpage/usecase.html", context)


def create_issue_report(request):
    """
    This view is called by muo search using ajax to display the report issue popup
    """
    if request.method == "POST":
        # read the usecase_id that triggered this action
        usecase_id = request.POST.get('usecase_id')
        usecase = get_object_or_404(UseCase, pk=usecase_id)

        # Render issue report form and default initial values, if any
        ModelForm = autocomplete_light.modelform_factory(IssueReport, fields=('usecase', 'usecase_duplicate', 'description', 'type'))
        form = ModelForm()

        context = dict(
            form=form,
            usecase=usecase,
        )
        return TemplateResponse(request, "frontpage/create_issue_report.html", context)
    else:
        raise Http404("Invalid access using GET request!")


def process_issue_report(request):
    """
    Handle adding new report created using muo search popup
    """
    if request.method == 'POST':

        ModelForm = autocomplete_light.modelform_factory(IssueReport, fields=('usecase', 'usecase_duplicate', 'description', 'type'))
        form = ModelForm(request.POST, request.FILES)
        if form.is_valid():
            new_object = form.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Report %s has been created will be reviewed by our reviewers" % new_object.name)
        else:
            # submitted form is invalid
            errors = ["%s: %s" % (form.fields[field].label, error[0]) for field, error in form.errors.iteritems()]
            errors = '<br/>'.join(errors)
            messages.add_message(request, messages.ERROR, mark_safe("Invalid report content!<br/>%s" % errors) )

        return HttpResponseRedirect(reverse('frontpage:index'))

    else:
        raise Http404("Invalid access using GET request!")

