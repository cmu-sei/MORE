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
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
import time
from muo.models import MUOContainer, MisuseCase, UseCase
from django.contrib.auth.models import User, Permission
from django.core import mail
from muo_mailer import constants

"""
These test cases are to test the mailing functionality

"""
class TestMUOMailer(TestCase):
    """
    This class is the test suite for the MUOContainer model class. It contains
    test cases for the custom methods in the MUOContainer model which are not
    related to the custom MUOs.
    """

    def setUp(self):
        """
        This method does the general setup needed for the test methods.
        For now it just creates a MUOContainer object, but can be used to
        do any default settings
        """
        muo_container_type = ContentType.objects.get(app_label='muo', model='muocontainer')
        perm = Permission.objects.get(codename='can_approve', content_type = muo_container_type)

        self.reject_msg = "This MUO is rejected!"
        self.reviewer = User(username='reviewer')
        self.reviewer.save()
        self.reviewer.user_permissions.add(perm)

        self.user = User(username='client1')
        self.user.save()

        misuse_case = MisuseCase()

        misuse_case.save()

        muo_container = MUOContainer.objects.create(misuse_case = misuse_case)  # MUOContainer cannot be created without misuse case
        muo_container.save()
        # The id field is auto incremental and we need to know the id of the currently created object
        self.current_id = muo_container.id

        use_case = UseCase(muo_container=muo_container)  # Usecase cannot be created without MUOContainer
        use_case.save()  # save in the database


    def get_muo_container(self, status):
        """
        This method sets the status of the MUOContainer object with the one
        received in arguments.
        """

        muo_container = MUOContainer.objects.get(pk=self.current_id)
        muo_container.status = status
        muo_container.created_by = self.user
        muo_container.misuse_case.misuse_case_type = 'new'
        muo_container.save()
        return muo_container

    def test_action_approve_with_status_in_review(self):
        """
        This is a positive test case
        'action_approve' should set the status to 'approved' when called on a MUOContainer object with status 'in_review'.
        """

        muo_container = self.get_muo_container('in_review')
        muo_container.action_approve()
        time.sleep(1) # sleep to allow the thread that sends the email to go first
        self.assertEqual(len(mail.outbox), 1)
        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, constants.MUO_ACCEPTED_SUBJECT)


    def test_action_reject_with_status_in_review(self):
        muo_container = self.get_muo_container('in_review')
        muo_container.action_reject(self.reject_msg)
        time.sleep(1) # sleep to allow the thread that sends the email to go first
        self.assertEqual(len(mail.outbox), 1)
        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, constants.MUO_REJECTED_SUBJECT)


    def test_action_submit_for_review(self):
        muo_container = self.get_muo_container('draft')
        muo_container.action_submit()
        time.sleep(1) # sleep to allow the thread that sends the email to go first
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, constants.MUO_SUBMITTED_FOR_REVIEW_SUBJECT)



