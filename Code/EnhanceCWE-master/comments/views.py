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
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.http import Http404

import django_comments
from django_comments.views.moderation import perform_delete


@login_required
def delete(request, comment_id, next=None):
    """
    This is an ajax view to delete a comment
    """
    comment = get_object_or_404(django_comments.get_model(), pk=comment_id, site__pk=settings.SITE_ID)

    if request.is_ajax():
        # comment can only be deleted by the owner or a moderator
        if not (comment.user.id == request.user.id or request.user.has_perm('django_comments.can_moderate')):
            raise Http404("User not allowed to delete this comment!")

        # Flag the comment as deleted instead of actually deleting it.
        perform_delete(request, comment)
        return JsonResponse({'comment_id': comment_id, 'is_removed': comment.is_removed})

    # Render a form on GET
    else:
        raise Http404()

