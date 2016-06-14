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
from django.contrib.auth.models import Group, User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from allauth.account.models import EmailAddress

# Adds a boolean field 'is_auto_assign_client' to the Groups
if not hasattr(Group, 'is_auto_assign_client'):
    field=models.BooleanField(default=False, verbose_name=_('Auto Assign to Clients'))
    field.contribute_to_class(Group, 'is_auto_assign_client')

# Adds a boolean field 'is_auto_assign_contributors' to the Groups
if not hasattr(Group, 'is_auto_assign_contributors'):
    field=models.BooleanField(default=False, verbose_name=_('Auto Assign to Contributors'))
    field.contribute_to_class(Group, 'is_auto_assign_contributors')

# Adds a boolean field 'requested_role' to the EmailAddress
if not hasattr(EmailAddress, 'requested_role'):
    field = models.CharField(max_length=20, choices=[('contributor', 'Contributor'), ('client', 'Client')], default='contributor')
    field.contribute_to_class(EmailAddress, 'requested_role')
