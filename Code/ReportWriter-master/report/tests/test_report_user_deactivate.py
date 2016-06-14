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
from django.contrib.auth.models import User
from report.models import Report


class TestUserDeactivation(TestCase):
    """
    This class is the test suite to test the method of user deactivation
    """
    def setUp(self):

        self.user = User(username='client1')
        self.user.save()
        report = Report.objects.create(title="Report1", description="This is a test report")
        report.save()
        self.report = report
        self.current_id = report.id

    def set_report(self, status):
        """
        This method sets the status of the MUOContainer object with the one
        received in arguments.
        """

        report = Report.objects.get(pk=self.current_id)
        report.status = status
        report.created_by = self.user
        report.save()
        return report

    def set_user_deactivation(self):
        self.user.is_active = False
        self.user.save()

    def test_user_deactivation_draft_report(self):
        """
        This is a positive test case
        This is a test case which sees that the muo container written by the user which is in draft state gets deleted
        if the user gets deactivated
        """

        self.set_report('draft')
        self.set_user_deactivation()
        report = Report.objects.filter(status__in=['draft', 'rejected', 'in_review'])
        self.assertFalse(report.exists())

    def test_user_deactivation_inreview_report(self):
        """
        This is a positive test case
        This is a test case which sees that the muo container written by the user which is in_review state gets deleted
        if the user gets deactivated
        """

        self.set_report('in_review')
        self.set_user_deactivation()
        report = Report.objects.filter(status__in=['draft', 'rejected', 'in_review'])
        self.assertFalse(report.exists())

    def test_user_deactivation_rejected(self):
        """
        This is a positive test case
        This is a test case which sees that the muo container written by the user which is in rejected state gets deleted
        if the user gets deactivated
        """
        self.set_report('rejected')
        self.set_user_deactivation()
        report = Report.objects.filter(status__in=['draft', 'rejected', 'in_review'])
        self.assertFalse(report.exists())


    def test_user_deactivation_approved(self):
        """
        This is a test case which sees that the muo container written by the user which is in approved state does not
        get deleted if the user gets deactivated
        """

        self.set_report('approved')
        self.set_user_deactivation()
        report = Report.objects.filter(status__in=['approved'])
        self.assertTrue(report.exists())






