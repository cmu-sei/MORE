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
from django.core import mail
from django.test import TestCase
from django.contrib.auth import get_user_model
from muo_mailer.models import MailerProfile

class MailerProfileTest(TestCase):

    def test_mailer_profiel_creation(self):
        # test creating mailer profile after creating a user
        user = get_user_model().objects.create(username="user")
        mailer_profile = MailerProfile.objects.filter(user=user)
        self.assertTrue(mailer_profile.exists(), "Failed to create mailer profile for user")

        # test deleting mailer profile after deleting a user
        user.delete()
        mailer_profile = MailerProfile.objects.filter(user=user)
        self.assertFalse(mailer_profile.exists(), "Failed to delete mailer profile after deleting user")


class EmailTest(TestCase):

    def test_send_email(self):
        # Send message.
        mail.send_mail('Subject here', 'Here is the message.',
            'enhancedcwe@gmail.com', ['example@gmail.com'],
            fail_silently=False)
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)
        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, 'Subject here')

