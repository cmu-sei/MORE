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
from django_comments.forms import CommentDetailsForm
from django.conf import settings

# duplicate identification period is set to -1 by default, which means duplicates are allowed all the time
COMMENT_DUPLICATE_IDENTIFICATION_PERIOD = getattr(settings, "COMMENT_DUPLICATE_IDENTIFICATION_PERIOD", 15)
COMMENT_DUPLICATE_ALLOWED = getattr(settings, "COMMENT_DUPLICATE_ALLOWED", True)

def check_for_duplicate_comment(self, new):
    """
    Check that a submitted comment isn't a duplicate. This might be caused
    by someone posting a comment twice. If it is a dup, silently return the *previous* comment.
    """
    if not COMMENT_DUPLICATE_ALLOWED:
        possible_duplicates = self.get_comment_model()._default_manager.using(
            self.target_object._state.db
        ).filter(
            content_type=new.content_type,
            object_pk=new.object_pk,
            user_name=new.user_name,
            user_email=new.user_email,
            user_url=new.user_url,
            is_removed=False,
        )
        for old in possible_duplicates:
            if old.comment == new.comment and \
                            (new.submit_date - old.submit_date).total_seconds() <= COMMENT_DUPLICATE_IDENTIFICATION_PERIOD:
                return old
    return new

# Monkey patch checking for duplicates
CommentDetailsForm.check_for_duplicate_comment = check_for_duplicate_comment
