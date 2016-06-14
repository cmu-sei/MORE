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
from muo.models import MUOContainer, MisuseCase, UseCase
from cwe.models import CWE
from django.contrib.auth.models import User


class MUOSignalsTest(TestCase):

    def setUp(self):
        test_user = User(username='test_user')
        test_user.save()
        self.user = test_user

        cwe1 = CWE(code=1, name='CWE-1')
        cwe1.save()
        misuse_case = MisuseCase()
        misuse_case.save()
        misuse_case.cwes.add(*[cwe1])

        muo_container = MUOContainer.objects.create(misuse_case=misuse_case, created_by=self.user)
        muo_container.save()
        muo_container.cwes.add(*[cwe1])

        use_case = UseCase(muo_container=muo_container)  # Usecase cannot be created without MUOContainer
        use_case.save()  # save in the database

        self.muo_container = muo_container


    # This is to test to check if signals are generated when muo gets accepted
    @patch('muo.signals.muo_accepted.send')
    def test_muo_accepted_signal_triggered(self, mock):
        self.muo_container.status = 'in_review'
        self.muo_container.action_approve(self.user)
        # Check that the signal was called.
        self.assertTrue(mock.called)
        # Check that your signal was called only once.
        self.assertEqual(mock.call_count, 1)

    # This is to test to check if signals are generated when muo gets rejected
    @patch('muo.signals.muo_rejected.send')
    def test_muo_rejected_signal_triggered(self, mock):
        self.muo_container.status = 'in_review'
        self.muo_container.action_reject("reason",self.user)
        # Check that the signal was called.
        self.assertTrue(mock.called)
        # Check that the signal was called only once.
        self.assertEqual(mock.call_count, 1)

    # # This is to test to check if signals are generated when muo is voted up
    # @patch('muo.signals.muo_voted_up.send')
    # def test_muo_votedup_signal_triggered(self, mock):
    #     # TODO the action for voted up should be invoked
    #     # muo_container.(method name)
    #     # Check that the signal was called.
    #     self.assertTrue(mock.called)
    #     # Check that the signal was called only once.
    #     self.assertEqual(mock.call_count, 1)
    #
    # # This is to test to check if signals are generated when muo is voted down
    # @patch('muo.signals.muo_voted_down.send')
    # def test_muo_voteddown_signal_triggered(self, mock):
    #     # TODO the action for voted down should be invoked
    #     # muo_container.method_name
    #     # Check that the signal was called.
    #     self.assertTrue(mock.called)
    #     # Check that the signal was called only once.
    #     self.assertEqual(mock.call_count, 1)
    #
    # @patch('muo.signals.muo_commented.send')
    # def test_muo_commented_signal_triggered(self, mock):
    #     # TODO the action for muo commented should be invoked
    #     # muo_container.method_name
    #     # Check that the signal was called.
    #     self.assertTrue(mock.called)
    #     # Check that the signal was called only once.
    #     self.assertEqual(mock.call_count,1)


    @patch('muo.signals.muo_submitted_for_review.send')
    def test_muo_submitted_for_review_signal_triggered(self, mock):
        self.muo_container.status = 'draft'
        self.muo_container.action_submit()
        # Check that the signal was called.
        self.assertTrue(mock.called)
        # Check that the signal was called only once.
        self.assertEqual(mock.call_count, 1)
