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
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from allauth.account.models import EmailAddress
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from register.tests import RegisterHelper

@override_settings(
    ACCOUNT_EMAIL_VERIFICATION='mandatory',
    ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION='True',
    SET_STAFF_ON_REGISTRATION=True)
class RegisterApprovalTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(RegisterApprovalTest, cls).setUpClass()
        os.environ['RECAPTCHA_TESTING'] = 'True'

    @classmethod
    def tearDownClass(cls):
        super(RegisterApprovalTest, cls).tearDownClass()
        os.environ['RECAPTCHA_TESTING'] = 'False'


    def setUp(self):
        self.signup_url = '%s%s' % (self.live_server_url, reverse('account_signup'))
        self.login_url = '%s%s' % (self.live_server_url, reverse('account_login'))
        self.login_redirect_url = '%s%s' % (self.live_server_url, settings.LOGIN_REDIRECT_URL)

        self.selenium = webdriver.Firefox()
        super(RegisterApprovalTest, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(RegisterApprovalTest, self).tearDown()

    def test_approve_request(self):
        # Create admin
        RegisterHelper.create_superuser()
        RegisterHelper.fill_login_form(self.selenium, self.login_url, admin=True)
        RegisterHelper.submit_login_form(self.selenium)

        # Create user
        user = RegisterHelper.create_user(approved=False)
        # Get EmailAddress URL
        email_obj = EmailAddress.objects.filter(user=user)[0]
        assert email_obj.admin_approval != 'approved', 'EmailAddress is already approved when created!'

        email_url = reverse('admin:account_emailaddress_change', args=[email_obj.id])
        email_url = '%s%s' % (self.live_server_url, email_url)
        self.selenium.get(email_url)
        self.selenium.find_element_by_xpath('//input[@name="_approve"]').click()
        self.assertEqual(self.selenium.current_url, email_url)

        # Reload email_obj
        email_obj = EmailAddress.objects.get(pk=email_obj.pk)
        self.assertEqual(email_obj.admin_approval, 'approved', 'Failed to approve EmailAddress')

    def test_reject_request(self):
        # Create admin
        RegisterHelper.create_superuser()
        RegisterHelper.fill_login_form(self.selenium, self.login_url, admin=True)
        RegisterHelper.submit_login_form(self.selenium)

        # Create user
        user = RegisterHelper.create_user(approved=False)
        # Get EmailAddress URL
        email_obj = EmailAddress.objects.filter(user=user)[0]
        assert email_obj.admin_approval != 'rejected', 'EmailAddress is already rejected when created!'

        email_url = reverse('admin:account_emailaddress_change', args=[email_obj.id])
        email_url = '%s%s' % (self.live_server_url, email_url)
        self.selenium.get(email_url)

        # show rejection popup
        self.selenium.find_element_by_xpath('//button[@name="_reject"]').click()

        # wait for popup
        reject_textarea = WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.ID, "reject_reason_text"))
        )

        reject_button = self.selenium.find_element_by_xpath('//input[@name="_reject"]')
        self.assertFalse(reject_button.is_enabled(), 'Reject button is enabled even though reject reason is empty')

        reject_reason = "These are more than 15 characters"
        reject_textarea.send_keys(reject_reason)
        self.assertTrue(reject_button.is_enabled(), 'Reject button is disabled even after filling reject reason')

        reject_button.click()
        self.assertEqual(self.selenium.current_url, email_url)

        # Reload email_obj
        email_obj = EmailAddress.objects.get(pk=email_obj.pk)
        self.assertEqual(email_obj.admin_approval, 'rejected', 'Failed to reject EmailAddress')
        self.assertEqual(email_obj.reject_reason, reject_reason, 'Failed to update reject reason')


    def test_login_approval(self):
        RegisterHelper.fill_register_form(self.selenium, self.signup_url)
        RegisterHelper.submit_register_form(self.selenium)
        RegisterHelper.verify_email(self.live_server_url, self.selenium)

        # Test that user is redirected to login page after email confirmation
        self.assertEqual(self.selenium.current_url, self.login_url,
                         'Failed to redirect to login page after email confirmation')

        email_obj = EmailAddress.objects.filter(email=RegisterHelper.form_params.get('email'))[0]

        # Verify email is not approved
        self.assertEqual(email_obj.admin_approval, 'pending', 'Registration request is not in pending state by default')


        # Try to login before approving from admin
        RegisterHelper.fill_login_form(self.selenium, self.login_url)
        RegisterHelper.submit_login_form(self.selenium)
        self.assertEqual(self.selenium.current_url, self.login_url,
                         'Login succeeded even though admin did not approve registration request!')


        # Reject request
        email_count = len(mail.outbox)
        email_obj.action_reject("this is rejection reason")
        self.assertEqual(email_obj.admin_approval, 'rejected', 'Registration request rejection failed')

        # Verify rejection email was sent
        self.assertEqual(len(mail.outbox), email_count + 1, 'Registration rejection email failed to send')

        # Try to login after rejecting the request
        RegisterHelper.fill_login_form(self.selenium, self.login_url)
        RegisterHelper.submit_login_form(self.selenium)
        self.assertEqual(self.selenium.current_url, self.login_url,
                         'Login succeeded even after admin rejected registration request!')


        # Approve request
        email_count = len(mail.outbox)
        email_obj.action_approve()
        self.assertEqual(email_obj.admin_approval, 'approved', 'Registration request approval failed')

        # Verify approval email was sent
        self.assertEqual(len(mail.outbox), email_count + 1, 'Registration approval email failed to send')


        # Try to login after approving the request
        RegisterHelper.fill_login_form(self.selenium, self.login_url)
        RegisterHelper.submit_login_form(self.selenium)
        self.assertEqual(self.selenium.current_url, self.login_redirect_url,
                         'Login failed even after admin approved registration request!')


    def test_login_pre_approved(self):
        RegisterHelper.fill_register_form(self.selenium, self.signup_url)
        RegisterHelper.submit_register_form(self.selenium)

        email_obj = EmailAddress.objects.filter(email=RegisterHelper.form_params.get('email'))[0]
        email_obj.admin_approval = 'approved'
        email_obj.save()

        RegisterHelper.verify_email(self.live_server_url, self.selenium)

        # Test that user is redirected to login page after email confirmation as he is already approved
        self.assertEqual(self.selenium.current_url, self.login_redirect_url,
                         'Failed to redirect to login page after email confirmation of pre-approved user')
