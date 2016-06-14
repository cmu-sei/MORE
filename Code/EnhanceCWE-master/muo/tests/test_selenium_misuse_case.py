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
import time
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from allauth.account.models import EmailAddress
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException, NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from EnhancedCWE.settings_travis import SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT
from cwe.models import CWE
from muo.models import MisuseCase
from muo.models import UseCase
from muo.models import MUOContainer
from muo.models import IssueReport


class MisuseCaseManagement(StaticLiveServerTestCase):

    def _create_user(self, name, password, is_admin=False):
        email = "%s%s" % (name, "@example.com")
        user = get_user_model().objects.create(username=name,
                                               email=email,
                                               is_staff=True,
                                               is_active=True,
                                               is_superuser=is_admin
                                               )
        user.set_password(password)
        user.save()

        email_obj = EmailAddress.objects.create(user=user,
                                                email=email,
                                                primary=True,
                                                verified=True)
        if 'register_approval' in settings.INSTALLED_APPS:
            email_obj.admin_approval = 'approved'
        email_obj.save()

        return user

    def _assign_permissions_contributor(self, user):
        ct_keyword = ContentType.objects.get(app_label="cwe", model="keyword")
        ct_category = ContentType.objects.get(app_label="cwe", model="category")
        ct_cwe = ContentType.objects.get(app_label="cwe", model="cwe")
        ct_misuse_case = ContentType.objects.get(app_label="muo", model="misusecase")
        ct_use_case = ContentType.objects.get(app_label="muo", model="usecase")
        ct_issue_report = ContentType.objects.get(app_label="muo", model="issuereport")
        ct_tag = ContentType.objects.get(app_label="muo", model="tag")
        ct_muo = ContentType.objects.get(app_label="muo", model="muocontainer")

        contributor_permissions = [
            Permission.objects.get(content_type=ct_keyword, codename="add_keyword"),
            Permission.objects.get(content_type=ct_keyword, codename="change_keyword"),
            Permission.objects.get(content_type=ct_keyword, codename="delete_keyword"),

            Permission.objects.get(content_type=ct_category, codename="view_category"),
            Permission.objects.get(content_type=ct_category, codename="delete_category"),
            Permission.objects.get(content_type=ct_category, codename="change_category"),
            Permission.objects.get(content_type=ct_category, codename="add_category"),

            Permission.objects.get(content_type=ct_cwe, codename="view_cwe"),
            Permission.objects.get(content_type=ct_cwe, codename="delete_cwe"),
            Permission.objects.get(content_type=ct_cwe, codename="change_cwe"),
            Permission.objects.get(content_type=ct_cwe, codename="add_cwe"),

            Permission.objects.get(content_type=ct_tag, codename="change_tag"),
            Permission.objects.get(content_type=ct_tag, codename="view_tag"),
            Permission.objects.get(content_type=ct_tag, codename="delete_tag"),
            Permission.objects.get(content_type=ct_tag, codename="change_tag"),

            Permission.objects.get(content_type=ct_misuse_case, codename="add_misusecase"),
            Permission.objects.get(content_type=ct_misuse_case, codename="change_misusecase"),
            Permission.objects.get(content_type=ct_misuse_case, codename="delete_misusecase"),

            Permission.objects.get(content_type=ct_use_case, codename="add_usecase"),
            Permission.objects.get(content_type=ct_use_case, codename="change_usecase"),
            Permission.objects.get(content_type=ct_use_case, codename="delete_usecase"),

            Permission.objects.get(content_type=ct_issue_report, codename="add_issuereport"),
            Permission.objects.get(content_type=ct_issue_report, codename="change_issuereport"),
            Permission.objects.get(content_type=ct_issue_report, codename="delete_issuereport"),

            Permission.objects.get(content_type=ct_muo, codename="can_view_all"),
            # Permission.objects.get(content_type=ct_muo, codename="can_reject"),
            Permission.objects.get(content_type=ct_muo, codename="delete_muocontainer"),
            Permission.objects.get(content_type=ct_muo, codename="can_edit_all"),
            Permission.objects.get(content_type=ct_muo, codename="change_muocontainer"),
            # Permission.objects.get(content_type=ct_muo, codename="can_approve"),
            Permission.objects.get(content_type=ct_muo, codename="add_muocontainer"),
        ]
        user.user_permissions.add(*contributor_permissions)

    def _set_up_basic_test_data(self):
        # Create two users.
        self.user_admin = self._create_user(name="admin", password="admin", is_admin=True)
        self.user_client = self._create_user(name="client", password="client", is_admin=False)
        self.user_contributor = self._create_user(name="contributor", password="contributor", is_admin=False)
        self._assign_permissions_contributor(self.user_contributor)

        # Create CWEs.
        self.cwe_auth = CWE.objects.create(code=1, name="authentication bypass")
        self.cwe_access = CWE.objects.create(code=2, name="file access denied")

    def _tear_down_all_test_data(self):
        # Reject all the MUO containers before deleting them.
        for muo in MUOContainer.objects.all():
            if muo.status != 'draft' and muo.status != 'rejected':
                muo.action_reject(reject_reason="In order to delete the test data.")
        # Delete all the MUO containers.
        MUOContainer.objects.all().delete()
        # Delete all the misuse cases
        MisuseCase.objects.all().delete()
        # Delete all the CWEs.
        CWE.objects.all().delete()
        # Delete the issue report.
        IssueReport.objects.all().delete()

    def _create_misuse_case(self, index, creator, cwe_list):
        misuse_case = MisuseCase.objects.create(
            misuse_case_description="Misuse case #"+str(index),
            misuse_case_primary_actor="Primary actor #"+str(index),
            misuse_case_secondary_actor="Secondary actor #"+str(index),
            misuse_case_precondition="Pre-condition #"+str(index),
            misuse_case_flow_of_events="Event flow #"+str(index),
            misuse_case_postcondition="Post-condition #"+str(index),
            misuse_case_assumption="Assumption #"+str(index),
            misuse_case_source="Source #"+str(index),
            created_by=creator
        )
        misuse_case.cwes.add(*cwe_list)
        return misuse_case

    def _create_muo(self, custom, status, muc, muc_type):
        muo = MUOContainer.objects.create(is_custom=custom,
                                          status=status,
                                          misuse_case=muc,
                                          misuse_case_type=muc_type
                                          )
        return muo

    def _create_use_case(self, index, muo, muc):
        UseCase.objects.create(
            use_case_description="Use Case #"+str(index),
            use_case_primary_actor="Primary actor #"+str(index),
            use_case_secondary_actor="Secondary actor #"+str(index),
            use_case_precondition="Pre-condition #"+str(index),
            use_case_flow_of_events="Event flow #"+str(index),
            use_case_postcondition="Post-condition #"+str(index),
            use_case_assumption="Assumption #"+str(index),
            use_case_source="Source #"+str(index),
            osr_pattern_type="ubiquitous",
            osr="Overlooked Security Requirement #"+str(index),
            muo_container=muo,
            misuse_case=muc
        )

    def _create_multiple_misuse_cases(self):
        # Create the misuse case and establish the relationship with the CWEs
        misuse_case_1 = self._create_misuse_case(1, self.user_admin, [self.cwe_auth])
        misuse_case_2 = self._create_misuse_case(2, self.user_contributor, [self.cwe_access])
        misuse_case_3 = self._create_misuse_case(3, self.user_client, [self.cwe_auth])

        # Create MUO containers.
        muo1 = self._create_muo(custom=False, status="draft", muc=misuse_case_1, muc_type="existing")
        muo2 = self._create_muo(custom=False, status="draft", muc=misuse_case_2, muc_type="existing")
        muo3 = self._create_muo(custom=False, status="draft", muc=misuse_case_3, muc_type="existing")

        # Create some use cases(with OSRs)
        self._create_use_case(1, muo1, misuse_case_1)
        self._create_use_case(2, muo1, misuse_case_1)
        self._create_use_case(3, muo2, misuse_case_2)
        self._create_use_case(4, muo3, misuse_case_3)

        # Approve the MUOs
        muo1.action_submit()
        muo1.action_approve()
        muo2.action_submit()
        muo2.action_approve()
        # muo3 is left not approved intentionally.

    def _is_element_present(self, by, value):
        try:
            expected_conditions.presence_of_element_located((by, value))(self.browser)
            return True
        except NoSuchElementException:
            return False
        except TimeoutException:
            return False

    def _are_elements_present(self, by, value):
        try:
            elements = self.browser.find_elements(by, value)
            return len(elements) > 0
        except NoSuchElementException:
            return False
        except TimeoutException:
            return False

    def _is_element_not_present(self, by, value):
        try:
            expected_conditions.presence_of_element_located((by, value))(self.browser)
            return False
        except NoSuchElementException:
            return True
        except TimeoutException:
            return True

    def _are_elements_not_present(self, by, value):
        try:
            elements = self.browser.find_elements(by, value)
            return len(elements) == 0
        except:
            return True

    def setUp(self):
        # Call the setUp() in parent class.
        super(MisuseCaseManagement, self).setUp()
        # Launch a browser.
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT)
        # Create test data.
        self._set_up_basic_test_data()

    def tearDown(self):
        # Call tearDown to close the web browser
        self.browser.quit()
        # Delete test data.
        # Reject all the MUO containers before deleting them.
        for muo in MUOContainer.objects.all():
            if muo.status == 'approved':
                muo.action_reject(reject_reason="In order to delete the test data.")
        # Delete all the MUO containers.
        MUOContainer.objects.all().delete()
        # Delete all the misuse cases
        MisuseCase.objects.all().delete()
        # Delete all the CWEs.
        CWE.objects.all().delete()
        # Delete the issue report.
        IssueReport.objects.all().delete()

        # Call the tearDown() in parent class.
        super(MisuseCaseManagement, self).tearDown()

    def _log_in_as_admin(self):
        # Open the login page.
        login_url = "%s%s" % (self.live_server_url, reverse('account_login'))
        self.browser.get(login_url)

        # Fill login information
        self.browser.find_element_by_id("id_login").send_keys("admin")
        self.browser.find_element_by_id("id_password").send_keys("admin")
        # Log in
        self.browser.find_element_by_xpath('//button[@type="submit"][contains(text(), "Sign In")]').click()

    def _log_in_as_contributor(self):
        # Open the login page.
        login_url = "%s%s" % (self.live_server_url, reverse('account_login'))
        self.browser.get(login_url)

        # Fill login information
        self.browser.find_element_by_id("id_login").send_keys("contributor")
        self.browser.find_element_by_id("id_password").send_keys("contributor")
        # Log in
        self.browser.find_element_by_xpath('//button[@type="submit"][contains(text(), "Sign In")]').click()

    def _log_out(self):
        logout_url = "%s%s" % (self.live_server_url, reverse('account_logout'))
        self.browser.get(logout_url)
        self.browser.find_element_by_xpath("//input[@type='submit']").click()

    def test_without_log_in(self):
        """
        Test Point:
            1). The misuse case column shows all the misuse cases(approved) for all the users
            according to the selected CWEs.
            2). The misuse case information is displayed correctly.
            3). The use case column shows all the use cases associated with the currently
            selected misuse case.
            4). The comment-related and "Report Isuse" are not displayed.
        """
        # Create test data.
        self._create_multiple_misuse_cases()
        # Open the home page.
        self.browser.get(self.live_server_url)
        # Click the "Get MUOs" button.
        self.browser.find_element_by_id("cwe-submit-button").click()

        # Verify: The misuse case column shows all the misuse cases(approved) for all the users
        # according to the selected CWEs.
        misuse_cases = self.browser.find_elements_by_xpath("//div[@class='slim-scroll-div']/div")
        self.assertEqual(len(misuse_cases), 2)
        # Verify: The use case column shows all the use cases associated with the currently
        # selected misuse case.
        use_cases = self.browser.find_elements_by_xpath("//div[@class='fat-scroll-div']/div")
        self.assertEqual(len(use_cases), 2)
        # Verify: Comment-related controls are not displayed.
        self.assertTrue(self._is_element_not_present(By.XPATH, "//a[@href='#comments-block-1']"))
        self.assertTrue(self._is_element_not_present(By.ID, "id_comment"))
        self.assertTrue(self._are_elements_not_present(By.XPATH, "//div[@class='comment-item']"))
        # Verify: "Report Issue" is not displayed.
        self.assertTrue(self._are_elements_not_present(By.XPATH, "//a[@href='#muo-modal']"))

    def test_with_admin(self):
        """
        Test Point:
            1). The misuse case column shows all the misuse cases(approved) for all the users
            according to the selected CWEs.
            2). The misuse case information is displayed correctly.
            3). The use case column shows all the use cases associated with the currently
            selected misuse case.
            4). The comment-related and "Report Isuse" are displayed.
        """
        # Create test data.
        self._create_multiple_misuse_cases()
        # Log in as admin.
        self._log_in_as_admin()
        # Open the home page.
        self.browser.get(self.live_server_url)
        # Click the "Get MUOs" button.
        self.browser.find_element_by_id("cwe-submit-button").click()

        # Verify: The misuse case column shows all the misuse cases for all the users
        # according to the selected CWEs.
        misuse_cases = self.browser.find_elements_by_xpath("//div[@class='slim-scroll-div']/div")
        self.assertEqual(len(misuse_cases), 2)
        # Verify: The use case column shows all the use cases associated with the currently
        # selected misuse case.
        use_cases = self.browser.find_elements_by_xpath("//div[@class='fat-scroll-div']/div")
        self.assertEqual(len(use_cases), 2)
        # Verify: Comment-related controls are displayed.
        self.assertTrue(self._is_element_present(By.XPATH, "//a[@href='#comments-block-1']"))
        self.assertTrue(self._is_element_present(By.ID, "id_comment"))
        # Verify: "Report Issue" is displayed.
        self.assertTrue(self._are_elements_present(By.XPATH, "//a[@href='#muo-modal']"))

    # def test_comments(self):
    #     """
    #     Test Point:
    #         1). One user cannot delete the commnets by another user.
    #         2). Admin can delete everyone's comment.
    #     """
    #     # Create test data.
    #     self._create_multiple_misuse_cases()
    #     # Log in as contributor.
    #     self._log_in_as_admin()
    #     # Open the home page.
    #     self.browser.get(self.live_server_url)
    #     # Click the "Get MUOs" button.
    #     self.browser.find_element_by_id("cwe-submit-button").click()
    #
    #     # Verify: The misuse case column shows all the misuse cases for all the users
    #     # according to the selected CWEs.
    #     misuse_cases = self.browser.find_elements_by_xpath("//div[@class='slim-scroll-div']/div")
    #     self.assertEqual(len(misuse_cases), 2)
    #     # Verify: The use case column shows all the use cases associated with the currently
    #     # selected misuse case.
    #     use_cases = self.browser.find_elements_by_xpath("//div[@class='fat-scroll-div']/div")
    #     self.assertEqual(len(use_cases), 2)
    #     # Verify: Comments can be added.
    #     # Append comments.
    #     comment_area = self.browser.find_element_by_xpath(
    #         "//div[@class='fat-scroll-div']/div[position()=1]/div[@class='comments-container']/div/form/textarea"
    #     )
    #     comment_area.send_keys("comment-1\n")
    #     comment_area.submit()
    #     time.sleep(5)   # Need to wait for a while to make sure the comments really go in.
    #     comment_area.send_keys("comment-2\n")
    #     comment_area.submit()
    #     # Check the comments.
    #     time.sleep(5)   # Need to wait for a while to make sure the comments really go in.
    #     comment_items = self.browser.find_elements_by_xpath("//div[@class='comment-item']")
    #     self.assertEqual(len(comment_items), 2)
    #     self.assertTrue(self._is_element_present(By.ID, "id_comment"))
    #     # Verify: "Report Issue" is displayed.
    #     self.assertTrue(self._are_elements_present(By.XPATH, "//a[@href='#muo-modal']"))
    #
    #     # Log out.
    #     self._log_out()
    #     time.sleep(5)
    #
    #     # Log in as contributor
    #     self._log_in_as_contributor()
    #     time.sleep(5)
    #     # Open the home page.
    #     self.browser.get(self.live_server_url)
    #     time.sleep(30)
    #     # Click the "Get MUOs" button.
    #     self.browser.find_element_by_id("cwe-submit-button").click()
    #     # The contributor can see admin's comments, but cannot delete them.
    #     comment_items = self.browser.find_elements_by_xpath("//div[@class='comment-item']")
    #     self.assertEqual(len(comment_items), 2)
    #     # There should be no "Delete".
    #     self._are_elements_not_present(By.XPATH, "//a[@class='delete-comment']")

    def test_report_issue(self):
        """
        Test Point:
            1). "Report issue" can pop up the issue reporting dialog.
            2). The "Use case duplicate" box can be displayed when "Duplicate" type is selected.
            3). "Close" and "Report" buttons are shown.
        """
        # Create test data.
        self._create_multiple_misuse_cases()
        # Log in as contributor.
        self._log_in_as_admin()
        # Open the home page.
        self.browser.get(self.live_server_url)
        # Click the "Get MUOs" button.
        self.browser.find_element_by_id("cwe-submit-button").click()

        # Click "Report Issue" link.
        self.browser.find_elements_by_xpath("//a[@href='#muo-modal']")[0].click()

        # Verify: The "Type" selection box is enabled.
        type_selection = self.browser.find_element_by_id("id_type")
        self.assertTrue(type_selection.is_enabled())
        options = type_selection.find_elements_by_xpath(".//option")
        self.assertTrue(options[0].get_attribute("textContent"), "---------")
        self.assertTrue(options[1].get_attribute("textContent"), "Incorrect Content")
        self.assertTrue(options[2].get_attribute("textContent"), "Spam")
        self.assertTrue(options[3].get_attribute("textContent"), "Duplicate")

        # Verify: By default, the "----------" option is selected.
        self.assertTrue(options[0].get_attribute("selected"), "true")
        # Verify: The "Usecase duplicate" box is displayed.
        self.assertFalse(self.browser.find_element_by_id("id_usecase_duplicate-autocomplete").is_displayed())
        # Verify: The "Description" box is enabled.
        self.assertTrue(self.browser.find_element_by_id("id_description").is_enabled())
        # Verify: When "----------" option is selected, the "Report" button is disabled.
        btn_report = self.browser.find_element_by_name("_report")
        self.assertTrue(not btn_report.is_enabled())

        # Select: "Incorrect Content"
        Select(webelement=self.browser.find_element_by_id("id_type")).select_by_visible_text("Incorrect Content")
        # Verify: The "Usecase duplicate" box is displayed.
        self.assertFalse(self.browser.find_element_by_id("id_usecase_duplicate-autocomplete").is_displayed())
        # Verify: The "Description" box is enabled.
        self.assertTrue(self.browser.find_element_by_id("id_description").is_enabled())
        # Verify: "Report" button is enabled.
        self.assertTrue(btn_report.is_enabled())

        # Select: "Spam"
        Select(webelement=self.browser.find_element_by_id("id_type")).select_by_visible_text("Spam")
        # Verify: The "Usecase duplicate" box is displayed.
        self.assertFalse(self.browser.find_element_by_id("id_usecase_duplicate-autocomplete").is_displayed())
        # Verify: The "Description" box is enabled.
        self.assertTrue(self.browser.find_element_by_id("id_description").is_enabled())
        # Verify: "Report" button is enabled.
        self.assertTrue(btn_report.is_enabled())

        # Select: "Duplicate"
        Select(webelement=self.browser.find_element_by_id("id_type")).select_by_visible_text("Duplicate")
        # Verify: The "Usecase duplicate" box is displayed.
        self.assertTrue(self.browser.find_element_by_id("id_usecase_duplicate-autocomplete").is_displayed())
        # Verify: The "Description" box is enabled.
        self.assertTrue(self.browser.find_element_by_id("id_description").is_enabled())
        # Verify: "Report" button is enabled.
        self.assertTrue(not btn_report.is_enabled())

        # Verify: Buttons to dismiss the window are enabled: "X" and "Close" buttons.
        close_buttons = self.browser.find_elements_by_xpath("//button[@data-dismiss='modal']")
        self.assertTrue(close_buttons[0].is_enabled())
        self.assertTrue(close_buttons[1].is_enabled())

    def test_regression_01(self):
        """
        Test Regression: Verify that the "Usecase duplicate" input box can be displayed after an issue
            state is changed.
        Defect ID: Unknown
        """
        # Create multiple misuse cases
        self._create_multiple_misuse_cases()
        # Create an issue report.
        uc1 = UseCase.objects.get(use_case_description="Use Case #1")
        IssueReport.objects.create(description="Issue Report #1", type="spam", usecase=uc1)

        # Open Page: Front page
        self.browser.get(self.live_server_url)
        # Log in
        self._log_in_as_admin()
        # Change the status of the issue report.
        self.browser.get("%s%s" % (self.live_server_url, "/app/muo/issuereport/"))
        # Click Link: "Issue/00001"
        self.browser.find_element_by_link_text("Issue/00001").click()
        # Click Button: "Investigate"
        self.browser.find_element_by_name("_investigate").click()

        # Now go and verify that the "Usecase duplicate" input box can still be shown correctly.
        # Open Page: Front page
        self.browser.get(self.live_server_url)
        # Click the "Get MUOs" button.
        self.browser.find_element_by_id("cwe-submit-button").click()

        # Click Button: "Report Issue"
        self.browser.find_element_by_xpath("//a[@data-original-title='Report Issue']").click()
        # Select: "Duplicate"
        Select(webelement=self.browser.find_element_by_id("id_type")).select_by_visible_text("Duplicate")
        # Verify: "Usecase duplicate:" input box is shown.
        self.assertTrue(self.browser.find_element_by_id("id_usecase_duplicate-wrapper") is not None)
        # Click Button: "Close"
        self.browser.find_element_by_xpath("//button[@class='btn btn-default pull-left']").click()

    def test_regression_02(self):
        """
        Test Point: Verify that the comment count is updated as a comment is posted.
        Defect ID: Unknown
        """
        # Create test data.
        self._create_multiple_misuse_cases()
        # Open Page: Front page
        self.browser.get(self.live_server_url)
        # Log in
        self._log_in_as_admin()
        # Open Page: Front page
        self.browser.get(self.live_server_url)
        # Click the "Get MUOs" button.
        self.browser.find_element_by_id("cwe-submit-button").click()

        # Verify: 0 comment
        elm_comment_counter = self.browser.find_element_by_xpath(
            "//div[@class='fat-scroll-div']/div[1]/div[@class='usecase-footer']/div[@class='pull-left']/a"
        )
        self.assertEqual(elm_comment_counter.get_attribute("textContent").strip(), "0 comments")
        # Enter Text: "Sample comment."
        self.browser.find_element_by_id("id_comment").send_keys("Sample comment.")
        self.browser.find_element_by_id("id_comment").submit()
        time.sleep(5)   # Wait for a while to make sure the submission is completely done.
        # Verify: 1 comment
        self.assertEqual(elm_comment_counter.get_attribute("textContent").strip(), "1 comments")

    def test_regression_03(self):
        """
        Test Point: When there is no misuse case, open the "Misuse Case" page should not
            pop up error message.
        """
        # To test this point, we should not have any misuse cases in the database, so we
        # just delete the test data.
        self._tear_down_all_test_data()
        # Open Page: "Misuse Case"
        self.browser.get(self.live_server_url)
        # Click the "Get MUOs" button.
        self.browser.find_element_by_id("cwe-submit-button").click()

        # Verify: No error alert box popped up.
        try:
            err_msg_box = self.browser.switch_to.alert
            err_msg_box.dismiss()
            no_err_msg_box = False
        except NoAlertPresentException:
            no_err_msg_box = True
        self.assertTrue(no_err_msg_box)
