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
from django.contrib.auth.models import User
from cwe.models import CWE
from muo.models import MisuseCase, UseCase, MUOContainer


class TestMUODeletion(TestCase):
    """
    This class is the test suite to test the deletion behavior of MisuseCase, UseCase and OSR
    """

    def setUp(self):
        """
        This method does the general setup needed for the test methods.
        For now it just creates a MUOContainer object, but can be used to
        do any default settings
        """
        self.author = User(username='author')
        self.author.save()

        # Set 1
        self.misuse_case_1 = MisuseCase()
        self.misuse_case_1.save()
        self.misuse_case_1_id = self.misuse_case_1.id

        self.muo_container_1 = MUOContainer.objects.create(misuse_case=self.misuse_case_1, status='draft')
        self.muo_container_1.save()
        self.muo_container_1_id = self.muo_container_1.id

        self.use_case_1 = UseCase(muo_container=self.muo_container_1)
        self.use_case_1.save()

        # Set 2
        self.misuse_case_2 = MisuseCase()
        self.misuse_case_2.save()
        self.misuse_case_2_id = self.misuse_case_2.id

        self.muo_container_2 = MUOContainer.objects.create(misuse_case=self.misuse_case_2, status='rejected')
        self.muo_container_2.save()
        self.muo_container_2_id = self.muo_container_2.id

        self.muo_container_3 = MUOContainer.objects.create(misuse_case=self.misuse_case_2, status='approved')
        self.muo_container_3.save()
        self.muo_container_3_id = self.muo_container_3.id

        self.use_case_2 = UseCase(muo_container=self.muo_container_2)
        self.use_case_2.save()

    def test_muo_deletion_with_draft_status_and_not_sharing_misusecase_with_other_muo_containers(self):
        """
        This method test the deletion of a muo container that is in draft state and not sharing the misuse case
        with any other container. After delete, the muo container should get deleted and also the corresponding
        misuse case should get deleted
        """
        self.muo_container_1.delete()

        self.assertRaises(MUOContainer.DoesNotExist, MUOContainer.objects.get, pk=self.muo_container_1_id)
        self.assertRaises(MisuseCase.DoesNotExist, MisuseCase.objects.get, pk=self.misuse_case_1_id)

    def test_muo_deletion_with_rejected_status_and_sharing_misusecase_with_other_muo_containers(self):
        """
        This method tests the deletion of a muo container that is in rejected state and has the associated
        misuse case which is also associated with some other misuse case. In this case, the muo container
        should get deleted but the associated misuse case should not be deleted
        """
        self.muo_container_2.delete()

        self.assertRaises(MUOContainer.DoesNotExist, MUOContainer.objects.get, pk=self.muo_container_2_id)
        self.assertIsNotNone(MisuseCase.objects.get(pk=self.misuse_case_2_id))

    def test_muo_deletion_with_approved_status(self):
        """
        This method tests the deletion of the muo container that is in approved state. On deleting the
        muo container in approved state, validation error is raised.
        """
        self.assertRaises(ValidationError, self.muo_container_3.delete)

    def test_muo_deletion_with_in_review_status(self):
        """
        This method test the deletion of a muo container that is in in_review state and not sharing the misuse case
        with any other container. After delete, the muo container should get deleted and also the corresponding
        misuse case should get deleted
        """
        self.muo_container_3.status = 'in_review'

        self.muo_container_3.delete()

        self.assertRaises(MUOContainer.DoesNotExist, MUOContainer.objects.get, pk=self.muo_container_3_id)
