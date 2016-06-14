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
from muo.models import MUOContainer, MisuseCase, UseCase


class TestUserDeactivation(TestCase):
    """
    This class is the test suite to test the method of user deactivation
    """
    def setUp(self):

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

    def set_muo_container(self, status):
        """
        This method sets the status of the MUOContainer object with the one
        received in arguments.
        """

        muo_container = MUOContainer.objects.get(pk=self.current_id)
        muo_container.status = status
        muo_container.created_by = self.user
        muo_container.save()
        return muo_container

    def set_user_deactivation(self):
        self.user.is_active = False
        self.user.save()

    def test_user_deactivation_draft_muos(self):
        """
        This is a positive test case
        This is a test case which sees that the muo container written by the user which is in draft state gets deleted
        if the user gets deactivated
        """

        self.set_muo_container('draft')
        self.set_user_deactivation()
        muo_container = MUOContainer.objects.filter(status__in=['draft', 'rejected', 'in_review'])
        self.assertFalse(muo_container.exists())

    def test_user_deactivation_inreview_muos(self):
        """
        This is a positive test case
        This is a test case which sees that the muo container written by the user which is in_review state gets deleted
        if the user gets deactivated
        """

        self.set_muo_container('in_review')
        self.set_user_deactivation()
        muo_container = MUOContainer.objects.filter(status__in=['draft', 'rejected', 'in_review'])
        self.assertFalse(muo_container.exists())

    def test_user_deactivation_rejected(self):
        """
        This is a positive test case
        This is a test case which sees that the muo container written by the user which is in rejected state gets deleted
        if the user gets deactivated
        """
        self.set_muo_container('rejected')
        self.set_user_deactivation()
        muo_container = MUOContainer.objects.filter(status__in=['draft', 'rejected', 'in_review'])
        self.assertFalse(muo_container.exists())


    def test_user_deactivation_approved(self):
        """
        This is a test case which sees that the muo container written by the user which is in approved state does not
        get deleted if the user gets deactivated
        """

        self.set_muo_container('approved')
        self.set_user_deactivation()
        muo_container = MUOContainer.objects.filter(status__in=['approved'])
        self.assertTrue(muo_container.exists())





