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
from django.http import HttpResponseForbidden, Http404, HttpResponseRedirect
from django.db.models import Q
import operator
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.safestring import mark_safe
from report.models import Report, IssueReport


def report_list(request):
    """
    This view is called by reports search using ajax to get the list of reports for a given search query
    """
    if not request.is_ajax():
        return HttpResponseForbidden()

    term = request.POST.get('term')
    query = []

    if term:
        if term.isdigit():
            query.append(Q(pk__exact=term))
            query.append(Q(cwes__code__exact=term))

        query.append(Q(name__icontains=term))
        query.append(Q(title__icontains=term))
        query.append(Q(description__icontains=term))
        query.append(Q(cwes__name__icontains=term))

        reports = Report.objects.approved().filter(reduce(operator.or_, query)).distinct()
    else:
        reports = Report.objects.approved()

    context = {'reports': reports}

    return TemplateResponse(request, "report/report_list.html", context)


def report_details(request, pk):
    report = Report.objects.get(pk=pk, status='approved')
    if not report:
        return Http404()

    context = {'report': report}
    return TemplateResponse(request, "report/report_details.html", context)



def create_issue_report(request):
    """
    This view is called by muo search using ajax to display the report issue popup
    """
    if request.method == "POST":
        # read the report_id that triggered this action
        report_id = request.POST.get('report_id')
        report = get_object_or_404(Report, pk=report_id)

        # Render issue report form and default initial values, if any
        ModelForm = autocomplete_light.modelform_factory(IssueReport, fields=('report', 'report_duplicate', 'description', 'type'))
        form = ModelForm()

        context = dict(
            form=form,
            report=report,
        )
        return TemplateResponse(request, "report/create_issue_report.html", context)
    else:
        raise Http404("Invalid access using GET request!")


def process_issue_report(request):
    """
    Handle adding new report created using muo search popup
    """
    if request.method == 'POST':

        ModelForm = autocomplete_light.modelform_factory(IssueReport, fields=('report', 'report_duplicate', 'description', 'type'))
        form = ModelForm(request.POST, request.FILES)
        if form.is_valid():
            new_object = form.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Issue Report %s has been created will be reviewed by our reviewers" % new_object.name)
        else:
            # submitted form is invalid
            errors = ["%s: %s" % (form.fields[field].label, error[0]) for field, error in form.errors.iteritems()]
            errors = '<br/>'.join(errors)
            messages.add_message(request, messages.ERROR, mark_safe("Invalid report content!<br/>%s" % errors) )

        return HttpResponseRedirect(reverse('report:report_details', kwargs={'pk': request.POST.get('report')}))

    else:
        raise Http404("Invalid access using GET request!")

