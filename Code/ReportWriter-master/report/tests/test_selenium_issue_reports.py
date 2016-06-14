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
from register.tests import RegisterHelper
from report.models import Report, IssueReport, CWE

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
        self.browser.implicitly_wait(10)
        # Log in.
        RegisterHelper.fill_login_form(
            selenium=self.browser,
            login_url="%s%s" % (self.live_server_url, reverse("account_login")),
            admin=True
        )
        RegisterHelper.submit_login_form(selenium=self.browser)


    def _set_up_test_data(self):
        # Create some CWEs. These CWEs will be used by all the test methods.
        cwe_01 = CWE(code=101, name='CWE 01')
        cwe_01.save()

        report_01 = Report(title='Sample report title', description='Sample report title')
        report_01.save()

        issue_report_01 = IssueReport(name="Issue/00001", type='incorrect', report=report_01)
        issue_report_01.save()

        return issue_report_01

    def tearDown(self):
        # Delete test data.
        self._tear_down_test_data()
        # Call tearDown to close the web browser
        self.browser.quit()
        # Call the tearDown() of parent class.
        super(IssueReportWorkflow, self).tearDown()

    def _tear_down_test_data(self):
        # Delete all the Reports
        Report.objects.all().delete()

        # Delete all the CWEs.
        CWE.objects.all().delete()

        # Delete the issue report.
        IssueReport.objects.all().delete()

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
        self.PAGE_URL_MUO_HOME = "/app/report/issuereport/1/"

        # Create test data
        issue_report = IssueReport.objects.get(name="Issue/00001")

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
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_report-autocomplete"]').is_enabled()
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
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_report-autocomplete"]').is_enabled()
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
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_report-autocomplete"]').is_enabled()
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

        self.PAGE_URL_MUO_HOME = "/app/report/issuereport/2/"

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
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_report-autocomplete"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if Description is disabled
        is_enabled = self.browser.find_element_by_id("id_description").is_enabled()
        self.assertEqual(is_enabled, True)

        # Check presence of reopen button
        btn_reopen_present = self._is_element_not_present(By.XPATH, '//*[@id="issuereport_form"]/div[2]/div[2]/input')
        self.assertEqual(btn_close_present, False)


