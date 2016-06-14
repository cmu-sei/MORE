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
from django.contrib.auth.models import Group, User
from allauth.account.models import EmailAddress

# Create your tests here.

class RegisterClientTest(TestCase):
    """
    This class is the test suite to test the methods of the CWESearchLocator class
    """



    def setUp(self):

        group = Group.objects.create(name="client1", is_auto_assign = False, is_auto_assign_contributors = False, is_auto_assign_client=True)
        group.save()

        group = Group.objects.create(name="client2", is_auto_assign = False, is_auto_assign_contributors = False, is_auto_assign_client=True)
        group.save()

        group = Group.objects.create(name="contributor1", is_auto_assign = False, is_auto_assign_contributors = True, is_auto_assign_client=False)
        group.save()

        group = Group.objects.create(name="contributor2", is_auto_assign = False, is_auto_assign_contributors = True, is_auto_assign_client=False)
        group.save()

        group = Group.objects.create(name="none1", is_auto_assign = False, is_auto_assign_contributors=False, is_auto_assign_client=False)
        group.save()

        group = Group.objects.create(name="none2", is_auto_assign = False, is_auto_assign_contributors=False, is_auto_assign_client=False)
        group.save()


    def tearDown(self):
        Group.objects.all().delete()

    def test_check_if_client_groups_assigned(self):
        """  This method checks the case that if the user is assigned a client role, then he is assigned all the roles
        for which is_auto_assign_client = True.
        Here we are checking the count and then the groups expected to be present and then the groups expected to be
        not present.
        """

        user = User.objects.create(username='test_user1')
        user.save()

        email = EmailAddress.objects.create(user_id=user.id, requested_role='client')
        email.save()

        group1 = str(user.groups.all()[0].name)
        group2 = str(user.groups.all()[1].name)

        num_of_groups_assigned = user.groups.all().count()

        self.assertEqual(num_of_groups_assigned, 2)

        self.assertEqual(group1, 'client1')
        self.assertEqual(group2, 'client2')



    def test_check_if_contributor_groups_assigned(self):
        """  This method checks the case that if the user is assigned a contributor role, then he is assigned all the
        roles for which is_auto_assign_contributors = True.
        Here we are checking the count and then the groups expected to be present and then the groups expected to be
        not present.
        """

        user = User.objects.create(username='test_user1')
        user.save()

        email = EmailAddress.objects.create(user_id=user.id, requested_role='contributor')
        email.save()

        group1 = str(user.groups.all()[0].name)
        group2 = str(user.groups.all()[1].name)

        num_of_groups_assigned = user.groups.all().count()

        self.assertEqual(num_of_groups_assigned, 2)

        self.assertEqual(group1, 'contributor1')
        self.assertEqual(group2, 'contributor2')
