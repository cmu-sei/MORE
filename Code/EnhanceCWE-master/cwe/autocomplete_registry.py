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

class CWEAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['^code', 'name']
    attrs = {'placeholder': 'CWE...'}
    model = CWE
    widget_attrs = {
        'class': 'modern-style',
    }
autocomplete_light.register(CWEAutocomplete)


class CategoryAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    attrs = {'placeholder': 'categories...'}
    model = Category
    widget_attrs = {
        'class': 'modern-style',
    }
autocomplete_light.register(CategoryAutocomplete)


class KeywordAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    attrs = {'placeholder': 'keywords...'}
    model = Keyword
    widget_attrs = {
        'class': 'modern-style',
    }
autocomplete_light.register(KeywordAutocomplete)


class UserAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['username', 'first_name', 'last_name']
    attrs = {'placeholder': 'users...'}
    model = User
    widget_attrs = {
        'class': 'modern-style',
    }
autocomplete_light.register(UserAutocomplete)



