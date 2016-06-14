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
from muo.models import MUOContainer, MisuseCase, UseCase
from django.contrib.auth.models import User

# Create your tests here.

class TestPublishUnpublish(TestCase):
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
        self.reject_msg = "This MUO is rejected!"
        self.reviewer = User(username='reviewer')
        self.reviewer.save()

        misuse_case = MisuseCase()
        misuse_case.save()

        # MUOContainer cannot be created without misuse case
        muo_container = MUOContainer.objects.create(misuse_case = misuse_case)
        muo_container.save()

        # The id field is auto incremental and we need to know the id of the currently created object
        self.current_id = muo_container.id

        # Usecase cannot be created without MUOContainer
        use_case = UseCase(muo_container=muo_container)
        use_case.save()  # save in the database


    def get_muo_container(self, status):
        """
        This method sets the status of the MUOContainer object with the one
        received in arguments.
        """

        muo_container = MUOContainer.objects.get(pk=self.current_id)
        muo_container.status = status
        muo_container.save()
        return muo_container


    # Test 'action_approve'

    def test_muo_published_after_approval(self):
        """
        This is a positive test case
        'action_approve' should set the MUO to publish status.
        """

        muo_container = self.get_muo_container('in_review')
        muo_container.action_approve()
        self.assertEqual(muo_container.status, 'approved')
        self.assertEqual(muo_container.is_published, True)


    def test_action_publish_with_status_draft(self):
        """
        This is a negative test case
        'action_set_publish' should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'draft'.
        """

        muo_container = self.get_muo_container('draft')
        with self.assertRaises(ValueError):
            muo_container.action_set_publish(True)


    def test_action_unpublish_with_status_draft(self):
        """
        This is a negative test case
        'action_set_publish' should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'draft'.
        """

        muo_container = self.get_muo_container('draft')
        with self.assertRaises(ValueError):
            muo_container.action_set_publish(False)


    def test_action_publish_with_status_in_review(self):
        """
        This is a negative test case
        Publishing a report should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'draft'.
        """

        muo_container = self.get_muo_container('in_review')
        with self.assertRaises(ValueError):
            muo_container.action_set_publish(True)


    def test_action_unpublish_with_status_in_review(self):
        """
        This is a negative test case
        Unpublishing a report should raise a 'ValueError' exception when called on a MUOContainer
        object with status 'in_review'.
        """

        muo_container = self.get_muo_container('in_review')
        with self.assertRaises(ValueError):
            muo_container.action_set_publish(False)


