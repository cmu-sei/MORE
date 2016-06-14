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

    def test_action_approve_with_status_in_review(self):
        """
        This is a positive test case
        'action_approve' should set the status to 'approved' when called on a Report object with status 'in_review'.
        """

        report = self.get_report('in_review')
        report.action_approve()
        self.assertEqual(report.status, 'approved')


    def test_action_approve_with_status_draft(self):
        """
        This is a negative test case
        'action_approve' should raise a 'ValueError' exception when called on a Report
        object with status 'draft'.
        """

        report = self.get_report('draft')
        self.assertRaises(ValueError, report.action_approve)


    def test_action_approve_with_status_rejected(self):
        """
        This is a negative test case
        'action_approve' should raise a 'ValueError' exception when called on a Report
        object with status 'rejected'.
        """

        report = self.get_report('rejected')
        self.assertRaises(ValueError, report.action_approve)


    def test_action_approve_with_status_approved(self):
        """
        This is a negative test case
        'action_approve' should raise a 'ValueError' exception when called on a Report
        object with status 'approved'.
        """

        report= self.get_report('approved')
        self.assertRaises(ValueError, report.action_approve)


    def test_action_approve_with_status_invalid(self):
        """
        This is a negative test case
        'action_approve' should raise a 'ValueError' exception when called on a Report
        object with an invalid status value.
        """

        report= self.get_report('XXX')
        self.assertRaises(ValueError, report.action_approve)


    def test_action_approve_with_valid_reviewer(self):
        """
        This is a positive test case
        'action_approve' should update the reviewed_by field if reviewer parameter is passed
        """

        report = self.get_report('in_review')
        report.action_approve(reviewer=self.reviewer)
        self.assertEqual(report.reviewed_by, self.reviewer)


    def test_action_approve_with_no_reviewer(self):
        """
        This is a positive test case
        'action_approve' should set the reviewer to None if no reviewer is passed, even if the container had a reviewer
        """

        report = self.get_report('in_review')
        report.action_approve(reviewer=self.reviewer)

        # re-fetch Report
        report = self.get_report('in_review')
        report.action_approve()

        self.assertIsNone(report.reviewed_by)


    # Test 'action_reject'

    def test_action_reject_with_status_in_review(self):
        """
        This is a positive test case
        'action_reject' should set the status to 'rejected' when called on a Report
        object with status 'in_review'.
        """

        report = self.get_report('in_review')
        report.action_reject(self.reject_msg)
        self.assertEqual(report.status, 'rejected')


    def test_action_reject_with_status_approved(self):
        """
        This is a positive test case
        'action_reject' should set the status to 'rejected' when called on a Report
        object with status 'approved'.
        """

        report = self.get_report('approved')
        report.action_reject(self.reject_msg)
        self.assertEqual(report.status, 'rejected')


    def test_action_reject_with_status_draft(self):
        """
        This is a negative test case
        'action_reject' should raise a 'ValueError' exception when called on a Report
        object with status 'draft'.
        """

        report = self.get_report('draft')
        self.assertRaises(ValueError, report.action_reject, self.reject_msg)


    def test_action_reject_with_status_rejected(self):
        """
        This is a negative test case
        'action_reject' should raise a 'ValueError' exception when called on a Report
        object with status 'rejected'.
        """

        report= self.get_report('rejected')
        self.assertRaises(ValueError, report.action_reject, self.reject_msg)


    def test_action_reject_with_status_invalid(self):
        """
        This is a negative test case
        'action_reject' should raise a 'ValueError' exception when called on a Report
        object with an invalid status value.
        """

        report = self.get_report('XXX')
        self.assertRaises(ValueError, report.action_reject, self.reject_msg)

    def test_action_reject_with_valid_reviewer(self):
        """
        This is a positive test case
        'action_reject' should update the reviewed_by field if reviewer parameter is passed
        """

        report = self.get_report('in_review')
        report.action_reject(self.reject_msg, reviewer=self.reviewer)
        self.assertEqual(report.reviewed_by, self.reviewer)


    def test_action_reject_with_no_reviewer(self):
        """
        This is a positive test case
        'action_reject' should set the reviewer to None if no reviewer is passed, even if the Report had a reviewer
        """

        report = self.get_report('in_review')
        report.action_reject(self.reject_msg, reviewer=self.reviewer)

        # re-fetch Report
        report = self.get_report('in_review')
        report.action_reject(self.reject_msg)

        self.assertIsNone(report.reviewed_by)


    def test_action_submit_with_status_draft(self):
        """
        This is a positive test case
        'action_submit' should set the status to 'in_review' when called on a Report
        object with status 'draft'.
        """

        report= self.get_report('draft')
        report.action_submit()

        self.assertEqual(report.status, 'in_review')


    def test_action_submit_with_status_approved(self):
        """
        This is a negative test case
        'action_submit' should raise a 'ValueError' exception when called on a Report
        object with status 'approved'.
        """

        report = self.get_report('approved')
        self.assertRaises(ValueError, report.action_submit)


    def test_action_submit_with_status_rejected(self):
        """
        This is a negative test case
        'action_submit' should raise a 'ValueError' exception when called on a Report
        object with status 'rejected'.
        """

        report = self.get_report('rejected')
        self.assertRaises(ValueError, report.action_submit)


    def test_action_submit_with_status_in_review(self):
        """
        This is a negative test case
        'action_submit' should raise a 'ValueError' exception when called on a Report
        object with status 'in_review'.
        """

        report = self.get_report('in_review')
        self.assertRaises(ValueError, report.action_submit)


    def test_action_submit_with_status_invalid(self):
        """
        This is a negative test case
        'action_submit' should raise a 'ValueError' exception when called on a Report
        object with an invalid status value.
        """

        report = self.get_report('XXX')
        self.assertRaises(ValueError, report.action_submit)


    # Test 'action_save_in_draft'

    def test_action_save_in_draft_with_status_in_review(self):
        """
        This is a positive test case
        'action_save_in_draft' should set the status to 'draft' when called on a Report
        object with status 'in_review'.
        """

        report = self.get_report('in_review')
        report.action_save_in_draft()
        self.assertEqual(report.status, 'draft')


    def test_action_save_in_draft_with_status_rejected(self):
        """
        This is a positive test case
        'action_save_in_draft' should set the status to 'draft' when called on a Report
        object with status 'rejected'.
        """

        report = self.get_report('rejected')
        report.action_save_in_draft()
        self.assertEqual(report.status, 'draft')


    def test_action_save_in_draft_with_status_approved(self):
        """
        This is a negative test case
        'action_save_in_draft' should raise a 'ValueError' exception when called on a Report
        object with status 'approved'.
        """

        report = self.get_report('approved')
        self.assertRaises(ValueError, report.action_save_in_draft)


    def test_action_save_in_draft_with_status_draft(self):
        """
        This is a negative test case
        'action_save_in_draft' should raise a 'ValueError' exception when called on a Report
        object with status 'draft'.
        """

        report = self.get_report('draft')
        self.assertRaises(ValueError, report.action_save_in_draft)


    def test_action_save_in_draft_with_status_invalid(self):
        """
        This is a negative test case
        'action_save_in_draft' should raise a 'ValueError' exception when called on a Report
        object with an invalid status value.
        """

        report = self.get_report('XXX')
        self.assertRaises(ValueError, report.action_save_in_draft)

