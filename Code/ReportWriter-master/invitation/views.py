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


class MySignupView(views.SignupView):

    def get_form_class(self):
        """ Store the token and email in the session """
        if 'token' in self.request.GET and 'email' in self.request.GET:
            self.request.session['invite_email'] = self.request.GET['email']
            self.request.session['invite_token'] = self.request.GET['token']
        return super(MySignupView, self).get_form_class()


views.signup = MySignupView.as_view()
