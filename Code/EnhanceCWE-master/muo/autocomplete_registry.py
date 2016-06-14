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
from .models import *
import autocomplete_light

class MisuseCaseAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['id', 'name']
    attrs = {'placeholder': 'Misuse Case...'}
    model = MisuseCase
    widget_attrs = {
        'class': 'modern-style',
    }
autocomplete_light.register(MisuseCaseAutocomplete)


class UseCaseAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['id', 'name']
    attrs = {'placeholder': 'Use Case...'}
    model = UseCase
    widget_attrs = {
        'class': 'modern-style',
    }
autocomplete_light.register(UseCaseAutocomplete)


class TagAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^name',]
    attrs = {'placeholder': 'Tag...'}
    model = Tag
    widget_attrs = {
        'class': 'modern-style',
    }
autocomplete_light.register(TagAutocomplete)
