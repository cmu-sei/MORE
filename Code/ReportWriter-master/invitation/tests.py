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
from django.core import mail
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from allauth.account.models import EmailAddress
from selenium import webdriver
import os
from register.tests import RegisterHelper
from .models import EmailInvitation


@override_settings(
    LOGIN_REDIRECT_URL='/app/',
    ACCOUNT_EMAIL_VERIFICATION='mandatory',
    ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION='True',
    SET_STAFF_ON_REGISTRATION=True)
class RegisterInvitationTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(RegisterInvitationTest, cls).setUpClass()
        os.environ['RECAPTCHA_TESTING'] = 'True'

    @classmethod
    def tearDownClass(cls):
        super(RegisterInvitationTest, cls).tearDownClass()
        os.environ['RECAPTCHA_TESTING'] = 'False'

    def setUp(self):
        self.signup_url = '%s%s' % (self.live_server_url, reverse('account_signup'))
        self.login_url = '%s%s' % (self.live_server_url, reverse('account_login'))
        self.login_redirect_url = '%s%s' % (self.live_server_url, settings.LOGIN_REDIRECT_URL)

        self.selenium = webdriver.Firefox()
        super(RegisterInvitationTest, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(RegisterInvitationTest, self).tearDown()

    def test_create_invitation(self):

        invitation = EmailInvitation.objects.create(email=RegisterHelper.form_params['email'])
        self.assertEqual(invitation.status, 'pending', 'Default invitation status is not equal to pending')
        self.assertIsNotNone(invitation.key, 'Failed to create an invitation key')

        # Verify invitation email was sent
        email_count = len(mail.outbox)
        invitation.send_invitation()
        self.assertEqual(len(mail.outbox), email_count + 1, 'Invitation email failed to send')

    def test_register_invited(self):
        invitation = EmailInvitation.objects.create(email=RegisterHelper.form_params['email'])
        signup_url = '%s?token=%s&email=%s' % (self.signup_url, invitation.key, invitation.email)

        RegisterHelper.fill_register_form(self.selenium, signup_url)
        RegisterHelper.submit_register_form(self.selenium)

        invitation = EmailInvitation.objects.get(pk=invitation.pk) # reload invitation object
        self.assertEqual(invitation.status, 'accepted', 'Invitation status was not updated to accepted after registration')

        email_obj = EmailAddress.objects.filter(email=invitation.email)[0]
        self.assertTrue(email_obj.verified, 'Email was not verified after signup with invitation token')

        if 'register_approval' in settings.INSTALLED_APPS:
            # Verify email is automatically approved if registered with invitation token
            self.assertEqual(email_obj.admin_approval, 'approved',
                             'Registration request was not automatically approved when registering with invitation token')

        self.assertEqual(self.selenium.current_url, self.login_redirect_url,
                         'Auto login failed after registering with invitation token!')
