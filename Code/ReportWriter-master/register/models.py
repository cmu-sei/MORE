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
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from .settings import SET_STAFF_ON_REGISTRATION

# Make user email field required
User._meta.get_field('email').null = False
User._meta.get_field('email').blank = False


# Adds a boolean field 'is_auto_assign' to the group
if not hasattr(Group, 'is_auto_assign'):
    field=models.BooleanField(default=False, verbose_name=_('Auto Assign'))
    field.contribute_to_class(Group, 'is_auto_assign')


@receiver(post_save, sender=User, dispatch_uid='add_user_to_default_groups')
def add_group_to_user(sender, instance, created, using, **kwargs):
    """
    This method adds users after saving them to default groups as defined by 'is_auto_assign'
    """
    if created:
        user = instance

        # Filter all those groups with assignable attribute set to True
        groups = list(Group.objects.filter(is_auto_assign=True))
        user.groups.add(*groups)

        if SET_STAFF_ON_REGISTRATION:
            user.is_staff = True
            user.save()


