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
from muo.models import MUOContainer, MisuseCase, UseCase, IssueReport
from django.contrib.auth.models import User

class TestIssueReport(TestCase):

    def setUp(self):
        """
        This method does the general setup needed for the test methods.
        For now it just creates a MUOContainer object and an issue report on that MUO Container
        """
        self.reviewer = User(username='reviewer')
        self.reviewer.save()
        misuse_case = MisuseCase()
        misuse_case.save()
        muo_container = MUOContainer.objects.create(misuse_case=misuse_case, status='approved')
        muo_container.save()
        use_case = UseCase(muo_container=muo_container)
        use_case.save()  # save in the database
        issue_report = IssueReport.objects.create(description="this is the issue", type="spam",
                                                 usecase=use_case)
        issue_report.save()
        self.issue_report = issue_report


    def get_issue_report(self, status):
        """
        This method sets the status of the Issue Report object with the one
        received in arguments.
        """
        self.issue_report.status = status
        self.issue_report.save()
        return self.issue_report

    def test_action_investigate(self):
        """
        This method checks if the state gets changed to investigating or not
        """
        issue_report = self.get_issue_report("open")
        issue_report.action_investigate(reviewer=self.reviewer)
        self.assertEqual(issue_report.status, 'investigating')
        self.assertEqual(issue_report.reviewed_by, self.reviewer)

    def test_action_resolve(self):
        """
        This method checks if the state gets changed to resolved
        """
        resolve_reason = "This issue is resolved"
        issue_report = self.get_issue_report("investigating")
        issue_report.action_resolve(reviewer = self.reviewer, resolve_reason=resolve_reason)
        self.assertEqual(issue_report.status,'resolved')
        self.assertEqual(issue_report.reviewed_by,self.reviewer)

    def test_action_open(self):
        """
        This method checks if the state gets changed to open or not
        """
        issue_report = self.get_issue_report("investigating")
        issue_report.action_open(reviewer=self.reviewer)
        self.assertEqual(issue_report.status,'open')
        self.assertEqual(issue_report.reviewed_by,self.reviewer)

    def test_action_reopen(self):
        """
        This method checks if the state gets changed to re-open or not
        """
        issue_report = self.get_issue_report("resolved")
        issue_report.action_reopen(reviewer=self.reviewer)
        self.assertEqual(issue_report.status,'reopened')
        self.assertEqual(issue_report.reviewed_by,self.reviewer)

    def test_action_investigate_negative(self):
        """
        This is a negative test case which tries to see if action_investigate method is called when the state is investigate
        It should throw an error
        """
        issue_report = self.get_issue_report("investigating")
        self.assertRaises(ValueError, issue_report.action_investigate)

    def test_action_resolve_negative(self):
        """
        This is a negative test case which tries to see if action_resolve method is called when the state is open
        It should throw an error
        """
        issue_report = self.get_issue_report("open")
        resolve_reason = "This is an issue"
        self.assertRaises(ValueError, issue_report.action_resolve,resolve_reason)

    def test_action_reopen_negative(self):
        """
        This is a negative test case which tries to see if action_reopen method is called when the state is open
        It should throw an error
        """
        issue_report = self.get_issue_report("open")
        self.assertRaises(ValueError, issue_report.action_reopen)

















