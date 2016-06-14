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
from allauth.account import views


class CaptchaLoginView(views.LoginView):

    def get_form_kwargs(self):
        """ Pass the request object to the form to be able to access the session """
        kwargs = super(CaptchaLoginView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

# This will be the login view
login = CaptchaLoginView.as_view()

# Routing logout and password_change to allauth
logout = views.logout
password_change = views.password_change
