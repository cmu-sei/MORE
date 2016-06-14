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
from django.contrib.admin.options import ModelAdmin

def get_list_display(self, request):
    """
    Patching the method to include the checkboxes while in popup mode.
    Return a sequence containing the fields to be displayed on the changelist.
    """
    if request.GET.get('_popup', False):
        return ['action_checkbox'] + list(self.list_display)
    else:
        return self.list_display


def get_list_display_links(self, request, list_display):
        """
        Patching the method to handle displaying the checkbox while in popup mode.
        Return a sequence containing the fields to be displayed as links
        on the changelist. The list_display parameter is the list of fields
        returned by get_list_display().
        """
        if self.list_display_links or self.list_display_links is None or not list_display:
            return self.list_display_links
        else:
            if request.GET.get('_popup', False):
                # Use the second item in list_display as link if checkbox is first element
                return list(list_display)[1:2]
            else:
                # Use only the first item in list_display as link
                return list(list_display)[:1]


ModelAdmin.get_list_display = get_list_display
ModelAdmin.get_list_display_links = get_list_display_links
