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
"""Add user created_by and modified_by foreign key refs to any model automatically.
   Almost entirely taken from https://github.com/Atomidata/django-audit-log/blob/master/audit_log/middleware.py"""
from django.db.models import signals
from django.utils.functional import curry

class WhodidMiddleware(object):
    def process_request(self, request):
        if not request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user = request.user
            else:
                user = None
 
            mark_whodid = curry(self.mark_whodid, user)
            signals.pre_save.connect(mark_whodid,  dispatch_uid = (self.__class__, request,), weak = False)
 
    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid =  (self.__class__, request,))
        return response
 
    def mark_whodid(self, user, sender, instance, **kwargs):
        if not getattr(instance, 'created_by_id', None):
            instance.created_by = user
        if hasattr(instance,'modified_by_id'):
            instance.modified_by = user
