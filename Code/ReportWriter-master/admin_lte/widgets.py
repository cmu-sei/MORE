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
"""
Form Widget classes specific to the Django admin site.
"""
from __future__ import unicode_literals

import copy

from django import forms
from django.contrib.admin.templatetags.admin_static import static
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models.deletion import CASCADE
from django.forms.utils import flatatt
from django.forms.widgets import Media, RadioFieldRenderer
from django.template.loader import render_to_string
from django.utils import six
from django.utils.encoding import force_text
from django.utils.html import (
    escape, format_html, format_html_join, smart_urlquote,
)
from django.utils.safestring import mark_safe
from django.utils.text import Truncator
from django.utils.translation import ugettext as _
import django.contrib.admin.widgets
from django.contrib.admin.widgets import FilteredSelectMultiple



class MyRelatedFieldWidgetWrapper(django.contrib.admin.widgets.RelatedFieldWidgetWrapper):
    """
    Overriding the RelatedFieldWidgetWrapper to add 'search related' button next to
    foreignkey and many2many fields in admin area.
    """

    def render(self, name, value, *args, **kwargs):
        from django.contrib.admin.views.main import IS_POPUP_VAR, TO_FIELD_VAR
        rel_opts = self.rel.to._meta
        info = (rel_opts.app_label, rel_opts.model_name)
        self.widget.choices = self.choices
        url_params = '&'.join("%s=%s" % param for param in [
            (TO_FIELD_VAR, self.rel.get_related_field().name),
            (IS_POPUP_VAR, 1),
        ])
        context = {
            'widget': self.widget.render(name, value, *args, **kwargs),
            'name': name,
            'url_params': url_params,
            'model': rel_opts.verbose_name,
        }
        # Customized by AdminLTE
        if not isinstance(self.widget, FilteredSelectMultiple):
            # Don't show the search related if the widget is of type FilteredSelectMultiple
            # similar to groups and permissions in user management view
            try:
                search_related_url = self.get_related_url(info, 'changelist')
                context.update(
                    can_search_related=True,
                    search_related_url=search_related_url,
                )
            except NoReverseMatch:
                # If object doesn't have a changelist view, then just pass
                pass

        if self.can_change_related:
            change_related_template_url = self.get_related_url(info, 'change', '__fk__')
            context.update(
                can_change_related=True,
                change_related_template_url=change_related_template_url,
            )
        if self.can_add_related:
            add_related_url = self.get_related_url(info, 'add')
            context.update(
                can_add_related=True,
                add_related_url=add_related_url,
            )
        if self.can_delete_related:
            delete_related_template_url = self.get_related_url(info, 'delete', '__fk__')
            context.update(
                can_delete_related=True,
                delete_related_template_url=delete_related_template_url,
            )
        return mark_safe(render_to_string(self.template, context))


# Monkeypatch it
django.contrib.admin.widgets.RelatedFieldWidgetWrapper = MyRelatedFieldWidgetWrapper
