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
from django.contrib import admin
from base.admin import BaseAdmin
from models import *
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponseRedirect
from django.conf.urls import url
import autocomplete_light
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
import re

@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    fields = ['name']
    search_fields = ['name']


class KeywordAdminForm(forms.ModelForm):
    """
    Creating a custom form for keyword to validate the name is a single word only
    """
    def clean_name(self):
        if len(self.cleaned_data["name"].split()) > 1:
            raise forms.ValidationError("Keyword name should only have a single word")

        if not re.match(r'^[\w]+$', self.cleaned_data["name"]):
            raise forms.ValidationError("Keyword name can only have alphanumeric characters or underscore")

        """ Check the keyword stemmed format doesn't already exist in the database """
        cwe_search = CWESearchLocator.get_instance()
        stemmed_name = cwe_search.stem_text([self.cleaned_data["name"].lower()])
        if stemmed_name:
            # stem_text() always returns a list. Get the first element
            stemmed_name = stemmed_name[0]
            if Keyword.objects.filter(name__exact=stemmed_name).exists():
                raise forms.ValidationError("Keyword stemmed name (%s) already exist!" % stemmed_name)
            else:
                self.cleaned_data["name"] = stemmed_name

        return self.cleaned_data["name"]


@admin.register(Keyword)
class KeywordAdmin(BaseAdmin):
    form = KeywordAdminForm
    fields = ['name']
    search_fields = ['name']


@admin.register(CWE)
class CWEAdmin(BaseAdmin):
    model = CWE
    form = autocomplete_light.modelform_factory(CWE, fields="__all__")
    fieldsets = [
        ('CWE', {'fields': ['code', 'name', 'description'],
                 'classes': ['box-col-md-12']}),

        ('Categories', {'fields': ['categories'],
                   'classes': ['box-col-md-12']}),

        ('keywords', {'fields': ['keywords'],
                   'classes': ['box-col-md-12']}),
    ]
    search_fields = ['name', 'code', 'categories__name', 'keywords__name']
    list_filter = ['categories', 'keywords', ('created_by', admin.RelatedOnlyFieldListFilter)]
    date_hierarchy = 'created_at'


    def get_urls(self):
        urls = super(CWEAdmin, self).get_urls()
        my_urls = [
            # url will be /admin/cwe/cwe/<id>/suggested_keyword
            url(r'\d+/suggested_keywords/$', self.admin_site.admin_view(self.suggested_keywords_view)),
        ]
        return my_urls + urls

    def suggested_keywords_view(self, request):
        """
        This view is called by cwe change_form using ajax to display the list of suggested keywords from a given text
        """
        if request.method == "POST":
            suggested_text = request.POST.get('suggest_textarea', '')
            suggested_text = suggested_text.lower()

            cwe_search = CWESearchLocator.get_instance()
            filtered_words = cwe_search.remove_stopwords(suggested_text)
            stemmed_words = cwe_search.stem_text(filtered_words)

            context = dict(
               # Include common variables for rendering the admin template.
               self.admin_site.each_context(request),
               keywords=stemmed_words,
            )
            return TemplateResponse(request, "admin/cwe/cwe/suggested_keywords.html", context)
        else:
            raise Http404("Invalid access using GET request!")

    # Override response_change method of admin/options.py to handle the click of
    # newly added buttons
    def response_change(self, request, obj, *args, **kwargs):
        """
            Override response_change method of admin/options.py to handle the click of 'Add Keywords' button
        """

        if "_add_keywords_button" in request.POST:

            # Get the metadata about self (it tells you app and current model)
            opts = self.model._meta

            # Get the primary key of the model object i.e. MUO Container
            pk_value = obj._get_pk_val()

            preserved_filters = self.get_preserved_filters(request)

            redirect_url = reverse('admin:%s_%s_change' %
                                       (opts.app_label, opts.model_name),
                                       args=(pk_value,))
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)

            self._add_suggested_keywords(request, obj)

            return HttpResponseRedirect(redirect_url)

        else:
            # Let super class 'ModelAdmin' handle rest of the button clicks i.e. 'save' 'save and continue' etc.
            return super(CWEAdmin, self).response_change(request, obj, *args, **kwargs)



    def _add_suggested_keywords(self, request, obj):
        """
            This method handles the logic of creating and assigning suggested keywords to the CWE
        """
        suggested_keywords = request.POST.getlist('suggested_keywords', None)

        if suggested_keywords:
            # get the list names of the already existing keywords in the database
            existing_keywords = Keyword.objects.values('name')
            existing_keywords = [kw['name'] for kw in existing_keywords]

            # keywords that do not exist in the database
            to_add_db = [kw for kw in suggested_keywords if kw not in existing_keywords]

            # Note that using bulk_create() is very efficient as it only requires a single database query,
            # but it will not call save(), pre_save() or post_save() on the object
            to_add_db_objs = []
            for kw in to_add_db:
                to_add_db_objs.append(Keyword(name=kw))
            Keyword.objects.bulk_create(to_add_db_objs)

            # get the list names of the already existing keywords in the current CWE object
            cwe_keywords = obj.keywords.values('name')
            cwe_keywords = [kw['name'] for kw in cwe_keywords]
            to_add_cwe = [kw for kw in suggested_keywords if kw not in cwe_keywords]

            for kw_name in to_add_cwe:
                kw_obj = Keyword.objects.get(name=kw_name)
                obj.keywords.add(kw_obj)

            if to_add_cwe:
                self.message_user(request, "Added %s new keywords to the CWE" % len(to_add_cwe), messages.SUCCESS)
            else:
                self.message_user(request, "Selected keywords are already assigned to this CWE!", messages.WARNING)
        else:
            self.message_user(request, "Sorry, no keywords were found!", messages.ERROR)
