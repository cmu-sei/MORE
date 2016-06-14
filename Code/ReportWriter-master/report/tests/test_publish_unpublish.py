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

# Create your tests here.

class TestReport(TestCase):
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

        report = Report.objects.create(title="Report1", description="This is a test report")
        report.save()
        self.report = report

    def get_report(self, status):
        """
        This method sets the status of the Report object with the one
        received in arguments.
        """
        self.report.status = status
        self.report.save()
        return self.report

    # Test 'action_approve'

    def test_report_published_after_approval(self):
        """
        This is a positive test case
        'action_approve' should set the report to publish status.
        """

        report = self.get_report('in_review')
        report.action_approve()
        self.assertEqual(report.status, 'approved')
        self.assertEqual(report.is_published, True)


    def test_action_publish_with_status_draft(self):
        """
        This is a negative test case
        'action_set_publish' should raise a 'ValueError' exception when called on a report
        object with status 'draft'.
        """

        report = self.get_report('draft')
        with self.assertRaises(ValueError):
            report.action_set_publish(True)


    def test_action_unpublish_with_status_draft(self):
        """
        This is a negative test case
        'action_set_publish' should raise a 'ValueError' exception when called on a report
        object with status 'draft'.
        """

        report = self.get_report('draft')
        with self.assertRaises(ValueError):
            report.action_set_publish(False)


    def test_action_publish_with_status_in_review(self):
        """
        This is a negative test case
        Publishing a report should raise a 'ValueError' exception when called on a report
        object with status 'draft'.
        """

        report = self.get_report('in_review')
        with self.assertRaises(ValueError):
            report.action_set_publish(True)


    def test_action_unpublish_with_status_in_review(self):
        """
        This is a negative test case
        Unpublishing a report should raise a 'ValueError' exception when called on a report
        object with status 'in_review'.
        """

        report = self.get_report('in_review')
        with self.assertRaises(ValueError):
            report.action_set_publish(False)

