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
from mock import patch
from report.models import Report
from django.contrib.auth.models import User

class ReportSignalsTest(TestCase):

    def setUp(self):
        test_user = User(username='test_user')
        test_user.save()
        self.user = test_user
        report = Report.objects.create(title="Test Report", description="This is meant for testing")
        report.save()
        self.report = report

    # This is to test to check if signals are generated when report gets accepted
    @patch('report.signals.report_accepted.send')
    def test_report_accepted_signal_triggered(self, mock):
        self.report.status = 'in_review'
        self.report.action_approve(self.user)
        # Check that the signal was called.
        self.assertTrue(mock.called)
        # Check that your signal was called only once.
        self.assertEqual(mock.call_count, 1)

    # This is to test to check if signals are generated when report gets rejected
    @patch('report.signals.report_rejected.send')
    def test_report_rejected_signal_triggered(self, mock):
        self.report.status = 'in_review'
        self.report.action_reject("reason",self.user)
        # Check that the signal was called.
        self.assertTrue(mock.called)
        # Check that the signal was called only once.
        self.assertEqual(mock.call_count, 1)

    # This is to test to check if signals are generated when report is submitted for review
    @patch('report.signals.report_submitted_review.send')
    def test_report_submitted_for_review_signal_triggered(self, mock):
        self.report.status = 'draft'
        self.report.action_submit()
        # Check that the signal was called.
        self.assertTrue(mock.called)
        # Check that the signal was called only once.
        self.assertEqual(mock.call_count, 1)


