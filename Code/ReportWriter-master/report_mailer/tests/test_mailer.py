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
from django.test import TestCase
from django.core.exceptions import ValidationError
from report.models import Report
from django.contrib.auth.models import User
from django.core import mail
import time
from report_mailer import constants

# Create your tests here.

class TestReportMailer(TestCase):
    """
    This class is the test suite for the Report model class.
    """

    def setUp(self):
        """
        This method does the general setup needed for the test methods.
        For now it just creates a Report object, but can be used to
        do any default settings
        """
        self.reject_msg = "This Report is rejected!"
        self.reviewer = User(username='reviewer')
        self.reviewer.save()
        self.user = User(username='client1')
        self.user.save()
        report = Report.objects.create(title="Report1", description="This is a test report")
        report.save()
        self.report = report
        self.report.created_by = self.user
        self.report.save()

    def get_report(self, status):
        """
        This method sets the status of the Report object with the one
        received in arguments.
        """
        self.report.status = status

        return self.report


    # Test 'action_approve'

    def test_action_approve_with_status_in_review(self):
        """
        This is a positive test case
        'action_approve' should set the status to 'approved' when called on a Report object with status 'in_review'.
        """

        report = self.get_report('in_review')
        report.action_approve()
        time.sleep(1) # sleep to allow the thread that sends the email to go first
        self.assertEqual(len(mail.outbox), 1)
        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, constants.REPORT_ACCEPTED_SUBJECT)

    def test_action_reject_with_status_in_review(self):
        report = self.get_report('in_review')
        report.action_reject(self.reject_msg)
        time.sleep(1) # sleep to allow the thread that sends the email to go first
        self.assertEqual(len(mail.outbox), 1)
        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, constants.REPORT_REJECTED_SUBJECT)

