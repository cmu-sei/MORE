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
from django.conf import settings
from django.http.response import HttpResponseBase
from django.utils import importlib
import six
from allauth.account.utils import perform_login as allauth_perform_login

# Keep reference of original perform login before it gets monkey patched
original_perform_login = allauth_perform_login

def perform_login(request, user, email_verification, redirect_url=None, signal_kwargs=None, signup=False):
    """
    This method adds hooks for other applications to add behaviors to the original perform_login found in allauth
    """

    extra_pre_login_steps = getattr(settings, 'ACCOUNT_EXTRA_PRE_LOGIN_STEPS', [])
    for step in extra_pre_login_steps:
        method = import_attribute(step)
        step_res = method(**locals())
        if isinstance(step_res, HttpResponseBase):
            return step_res

    # Original Result
    original_res = original_perform_login(request, user, email_verification, redirect_url=redirect_url, signal_kwargs=signal_kwargs, signup=signup)

    extra_post_login_steps = getattr(settings, 'ACCOUNT_EXTRA_POST_LOGIN_STEPS', [])
    for step in extra_post_login_steps:
        method = import_attribute(step)
        step_res = method(**locals())
        if isinstance(step_res, HttpResponseBase):
            return step_res

    return original_res


def import_attribute(path):
    """ Proper import of methods passed as string of full qualified name """
    assert isinstance(path, six.string_types)
    pkg, attr = path.rsplit('.', 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret


# Monkey patch perform login
from allauth.account import utils
utils.perform_login = perform_login
