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
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from EnhancedCWE.settings_travis import SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT
from register.tests import RegisterHelper
from cwe.models import CWE
from muo.models import UseCase
from muo.models import MisuseCase
from muo.models import MUOContainer
from muo.models import IssueReport
from selenium.common.exceptions import NoSuchElementException

class IssueReportWorkflow(StaticLiveServerTestCase):

    # The URLs of the CWE-related pages.
    PAGE_URL_MUO_HOME = "/app/muo/issuereport/1/"

    def setUp(self):
        # Create test data.
        self._set_up_test_data()
        # Create the admin.
        RegisterHelper.create_superuser()
        # Launch a browser.
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT)
        # Log in.
        RegisterHelper.fill_login_form(
            selenium=self.browser,
            login_url="%s%s" % (self.live_server_url, reverse("account_login")),
            admin=True
        )
        RegisterHelper.submit_login_form(selenium=self.browser)

    def tearDown(self):
        # Create test data.
        self._tear_down_test_data()
        # Call tearDown to close the web browser.
        self.browser.quit()
        # Call the tearDown() of parent class.
        super(IssueReportWorkflow, self).tearDown()

    def _set_up_test_data(self):
        # Create some CWEs. These CWEs will be used by all the test methods.
        cwe101 = CWE(code=101, name="101")
        cwe101.save()


    def _tear_down_test_data(self):
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

    def _create_issue_report(self, issue_report_status='open'):
        cwe101 = CWE.objects.get(code=101)

        # Create the misuse case and establish the relationship with the CWEs
        misuse_case = MisuseCase(
            misuse_case_description="Misuse case #1",
            misuse_case_primary_actor="Primary actor #1",
            misuse_case_secondary_actor="Secondary actor #1",
            misuse_case_precondition="Pre-condition #1",
            misuse_case_flow_of_events="Event flow #1",
            misuse_case_postcondition="Post-condition #1",
            misuse_case_assumption="Assumption #1",
            misuse_case_source="Source #1"
        )
        misuse_case.save()
        misuse_case.cwes.add(cwe101)  # Establish the relationship between the misuse case and CWEs

        # Create the MUO container for the misuse case and establish the relationship between the
        # MUO Container and CWEs.
        muo_container = MUOContainer(is_custom=False,
                                     status='draft',
                                     misuse_case=misuse_case,
                                     misuse_case_type="new"
                                     )
        muo_container.save()
        muo_container.cwes.add(cwe101)   # Establish the relationship between the muo container and cwes

        # Create some use cases(with OSRs)
        uc = UseCase(
            use_case_description="Use Case #1",
            use_case_primary_actor="Primary actor #1",
            use_case_secondary_actor="Secondary actor #1",
            use_case_precondition="Pre-condition #1",
            use_case_flow_of_events="Event flow #1",
            use_case_postcondition="Post-condition #1",
            use_case_assumption="Assumption #1",
            use_case_source="Source #1",
            osr_pattern_type="ubiquitous",
            osr="Overlooked Security Requirement #1",
            muo_container=muo_container,
        )
        uc.muo_container = muo_container
        uc.misuse_case = misuse_case
        uc.save()

        # START
        issue_report_01 = IssueReport(name="Issue/00001",
                                      active=1,
                                      description="sample description",
                                      resolve_reason = "/",
                                      usecase = uc,
                                      status = issue_report_status)
        issue_report_01.save()
        # END

        return issue_report_01

    def _is_element_not_present(self, by, value):
        try:
            expected_conditions.presence_of_element_located((by, value))
            return False
        except NoSuchElementException:
            return True

    def test_point_01_ui_check_open_report(self):
        """
        Test Point: Verify that the Issue Report page in 'Open' status works as expected.
        """
        self.PAGE_URL_MUO_HOME = "/app/muo/issuereport/1/"

        # Create test data
        issue_report = self._create_issue_report(issue_report_status='open')

        # Open Page: "Issue Report"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MUO_HOME))

        # Get the status
        status = self.browser.find_element_by_xpath("//*[@id='fieldset-1']/div/div[1]/div/div[2]/div/p").text

        # Check the number of items in Select Box
        type = self.browser.find_element_by_id("id_type")
        options = [x for x in type.find_elements_by_tag_name("option")]

        self.assertEqual(len(options), 4)

        # Match the exact names of the items in select box
        self.assertEqual(options[1].get_attribute("value"), 'incorrect')
        self.assertEqual(options[2].get_attribute("value"), 'spam')
        self.assertEqual(options[3].get_attribute("value"), 'duplicate')


        # Check if Use Case is disabled
        is_enabled = self.browser.find_element_by_id("id_usecase-autocomplete").is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if Description is disabled
        is_enabled = self.browser.find_element_by_id("id_description").is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if Investigate button is present
        btn_investigate_present = self._is_element_not_present(By.XPATH, '//*[@id="issuereport_form"]/div[2]/div[2]/input')
        self.assertEqual(btn_investigate_present, False)

        # Check if Delete button is present
        btn_delete_present = self._is_element_not_present(By.XPATH, '//*[@id="issuereport_form"]/div[2]/div[1]/a')
        self.assertEqual(btn_delete_present, False)

        # Reviewed at time should be None
        self.assertEqual(self.browser.find_element_by_xpath("//*[@id='fieldset-1']/div/div[6]/div/div[2]/div/p").text, '(None)')

        # Reviewed by should be None
        self.assertEqual(self.browser.find_element_by_xpath("//*[@id='fieldset-1']/div/div[6]/div/div[1]/div/p").text, '(None)')


        # Select an option in Type
        self.browser.find_element_by_xpath("//select[@id='id_type']/option[@value='incorrect']").click()


        # Click on investigate
        self.browser.find_element_by_xpath('//*[@id="issuereport_form"]/div[2]/div[2]/input').click()

        # Check the message on the next screen
        notification_message = self.browser.find_element_by_xpath('//*[@id="content"]/div/div/div').text
        self.assertEqual(notification_message, u'The issue is now being investigated.')

        # Reviewed by status changes.
        reviewed_by = self.browser.find_element_by_xpath('//*[@id="fieldset-1"]/div/div[6]/div/div[1]/div/p').text
        result = False
        if reviewed_by:
            result = True
        self.assertEqual(result, True)

        # Reviewed at status changes.
        reviewed_at = self.browser.find_element_by_xpath('//*[@id="fieldset-1"]/div/div[6]/div/div[2]/div/p').text
        result = False
        if reviewed_at:
            result = True
        self.assertEqual(result, True)

        # Status should be Investigating
        status = self.browser.find_element_by_xpath("//*[@id='fieldset-1']/div/div[1]/div/div[2]/div/p").text
        self.assertEqual(status, u'Investigating')

        # Check the number of items in Select Box
        type = self.browser.find_element_by_id("id_type")
        options = [x for x in type.find_elements_by_tag_name("option")]

        self.assertEqual(len(options), 4)

        # Match the exact names of the items in select box
        self.assertEqual(options[1].get_attribute("value"), 'incorrect')
        self.assertEqual(options[2].get_attribute("value"), 'spam')
        self.assertEqual(options[3].get_attribute("value"), 'duplicate')

        # Check if Use Case is disabled
        is_enabled = self.browser.find_element_by_id("id_usecase-autocomplete").is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if Description is disabled
        is_enabled = self.browser.find_element_by_id("id_description").is_enabled()
        self.assertEqual(is_enabled, True)

        # Check the presence of Resolve button
        btn_resolve_present = self._is_element_not_present(By.XPATH, '//*[@id="issuereport_form"]/div[2]/div[2]/button')
        self.assertEqual(btn_investigate_present, False)

        # Check the presence of Open button
        btn_resolve_present = self._is_element_not_present(By.XPATH, '//*[@id="issuereport_form"]/div[2]/div[2]/input')
        self.assertEqual(btn_investigate_present, False)

        # Check if Delete button is present
        btn_delete_present = self._is_element_not_present(By.XPATH, '//*[@id="issuereport_form"]/div[2]/div[1]/a')
        self.assertEqual(btn_delete_present, False)

        # Click on Open
        self.browser.find_element_by_xpath('//*[@id="issuereport_form"]/div[2]/div[2]/input').click()

        # Check the message on the next screen
        notification_message = self.browser.find_element_by_xpath('//*[@id="content"]/div/div/div').text
        self.assertEqual(notification_message, u'The issue is now opened.')

        # Status should be open
        status = self.browser.find_element_by_xpath("//*[@id='fieldset-1']/div/div[1]/div/div[2]/div/p").text
        self.assertEqual(status, u'Open')

        # Check the type drop downs
        # Check the number of items in Select Box
        type = self.browser.find_element_by_id("id_type")
        options = [x for x in type.find_elements_by_tag_name("option")]

        self.assertEqual(len(options), 4)

        # Match the exact names of the items in select box
        self.assertEqual(options[1].get_attribute("value"), 'incorrect')
        self.assertEqual(options[2].get_attribute("value"), 'spam')
        self.assertEqual(options[3].get_attribute("value"), 'duplicate')

        # Check if Use Case is disabled
        is_enabled = self.browser.find_element_by_id("id_usecase-autocomplete").is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if Description is disabled
        is_enabled = self.browser.find_element_by_id("id_description").is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if Investigate button is present
        btn_investigate_present = self._is_element_not_present(By.XPATH, '//*[@id="issuereport_form"]/div[2]/div[2]/input')
        self.assertEqual(btn_investigate_present, False)


    def test_point_02_ui_check_resolve_issue(self):
        """
        Test Point: Verify the resolve issue workflow.
        """
        self.PAGE_URL_MUO_HOME = "/app/muo/issuereport/2/"

        # Create test data
        issue_report = self._create_issue_report(issue_report_status='open')

        # Open Page: "Issue Report"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MUO_HOME))

        # Select an option in Type
        self.browser.find_element_by_xpath("//select[@id='id_type']/option[@value='incorrect']").click()

        # Click on investigate
        self.browser.find_element_by_xpath('//*[@id="issuereport_form"]/div[2]/div[2]/input').click()

        # Click on resolve
        self.browser.find_element_by_xpath('//*[@id="issuereport_form"]/div[2]/div[2]/button').click()

        # Check presence of close button on pop up
        btn_close_present = self._is_element_not_present(By.XPATH, '//*[@id="resolve-model"]/div/div/div[3]/button')
        self.assertEqual(btn_close_present, False)

        # Check presence of Resolve button on pop up
        btn_resolve_present = self._is_element_not_present(By.XPATH, '//*[@id="resolve_button"]')
        self.assertEqual(btn_close_present, False)

        # Check if Resolve button is disabled because of blank description
        is_enabled = self.browser.find_element_by_xpath('//*[@id="resolve_button"]').is_enabled()
        self.assertEqual(is_enabled, False)

        # Check presence of resolve reason text box
        btn_close_present = self._is_element_not_present(By.XPATH, '//*[@id="resolve_reason_text"]')
        self.assertEqual(btn_close_present, False)

        # Put some description
        description = 'This is the resolve description.'
        self.browser.find_element_by_xpath('//*[@id="resolve_reason_text"]').send_keys(description)

        # Check if Resolve button is enabled because of 15 letter description
        is_enabled = self.browser.find_element_by_xpath('//*[@id="resolve_button"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Click on Resolve
        self.browser.find_element_by_xpath('//*[@id="resolve_button"]').click()

        # Check the message on the next screen
        notification_message = self.browser.find_element_by_xpath('//*[@id="content"]/div/div/div').text
        self.assertEqual(notification_message, u'The issue is now resolved because ' + description)

        # Check the type drop downs
        # Check the number of items in Select Box
        type = self.browser.find_element_by_id("id_type")
        options = [x for x in type.find_elements_by_tag_name("option")]

        self.assertEqual(len(options), 4)

        # Match the exact names of the items in select box
        self.assertEqual(options[1].get_attribute("value"), 'incorrect')
        self.assertEqual(options[2].get_attribute("value"), 'spam')
        self.assertEqual(options[3].get_attribute("value"), 'duplicate')

        # Check if Use Case is disabled
        is_enabled = self.browser.find_element_by_id("id_usecase-autocomplete").is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if Description is disabled
        is_enabled = self.browser.find_element_by_id("id_description").is_enabled()
        self.assertEqual(is_enabled, True)

        # Check presence of reopen button
        btn_reopen_present = self._is_element_not_present(By.XPATH, '//*[@id="issuereport_form"]/div[2]/div[2]/input')
        self.assertEqual(btn_close_present, False)






