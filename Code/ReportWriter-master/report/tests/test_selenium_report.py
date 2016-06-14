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
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from register.tests import RegisterHelper
from report.models import Report
from report.models import IssueReport, CWE


class ReportTestBase(StaticLiveServerTestCase):

    # The URLs of the Report-related pages.
    PAGE_URL_MUO_HOME = "/app/report/report/"

    def setUp(self):
        # Create test data.
        self.report = self._set_up_test_data()
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

        return report_01

    def tearDown(self):
        # Delete test data.
        self._tear_down_test_data()
        # Call tearDown to close the web browser
        self.browser.quit()
        # Call the tearDown() of parent class.
        super(ReportTestBase, self).tearDown()

    def _tear_down_test_data(self):
        # Delete all the Reports
        Report.objects.all().delete()

        # Delete all the CWEs.
        CWE.objects.all().delete()

    def _is_element_not_present(self, by, value):
        try:
            expected_conditions.presence_of_element_located((by, value))
            return False
        except NoSuchElementException:
            return True

    def test_point_01_ui_check_open_report(self):
        """
        Test Point: Verify that the Report in 'Open' status works as expected.
        """
        # Open Page: "Open Report"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MUO_HOME + '%s/' % self.report.pk))

        # Check if Name is disabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_name"]').is_enabled()
        self.assertEqual(is_enabled, False)
        print "tested 6"

        # Check if Status is disabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_status"]').is_enabled()
        self.assertEqual(is_enabled, False)

        # Check if title is enabled
        #is_enabled = self.browser.find_element_by_xpath('//*[@id="id_title"]').is_enabled()
        #self.assertEqual(is_enabled, True)

        # Check if Description is enabled
        #is_enabled = self.browser.find_element_by_xpath('//*[@id="id_description"]').is_enabled()
        #self.assertEqual(is_enabled, True)

        # Check if CWE Suggestion button is present
        btn_cwe_suggestion_present = self._is_element_not_present(By.XPATH,'//*[@id="cwe-suggestion-button"]' )
        self.assertEqual(btn_cwe_suggestion_present, False)

        # Check if Misuse Case custom button is present
        btn_misuse_custom_present = self._is_element_not_present(By.XPATH,'//*[@id="misusecase-custom"]' )
        self.assertEqual(btn_misuse_custom_present, False)

        # Check if Write my own Misuse Case Suggestion is present
        btn_misuse_suggestion_present = self._is_element_not_present(By.XPATH,'//*[@id="misusecase-suggestion"]')
        self.assertEqual(btn_misuse_suggestion_present, False)


    def test_point_02_ui_check_open_report(self):
        """
        Test Point: Verify that the click on Write my own misuse populates fields
        """
        # Open Page: "Open Report"
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_MUO_HOME + '%s/' % self.report.pk))

        # Click on the write my own misuse case
        self.browser.find_element_by_xpath('//*[@id="misusecase-custom"]').click()

        # Check if fields are populated are are editable
        # Check if Description for Misuse case is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_misuse_case_description"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if  misuse case primary actor is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_misuse_case_primary_actor"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if misuse case secondary actor is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_misuse_case_secondary_actor"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if misuse case precondition is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_misuse_case_precondition"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if misuse case flow of events is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_misuse_case_flow_of_events"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if misuse case post condition is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_misuse_case_postcondition"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if mis use case assumption is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_misuse_case_assumption"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if misuse case source is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_misuse_case_source"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if osr is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_osr"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if Description for Misuse case is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_use_case_description"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if  misuse case primary actor is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_use_case_primary_actor"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if misuse case secondary actor is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_use_case_secondary_actor"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if misuse case precondition is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_misuse_case_precondition"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if misuse case flow of events is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_use_case_flow_of_events"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if misuse case post condition is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_use_case_postcondition"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if mis use case assumption is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_use_case_assumption"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check if misuse case source is enabled
        is_enabled = self.browser.find_element_by_xpath('//*[@id="id_use_case_source"]').is_enabled()
        self.assertEqual(is_enabled, True)

        # Check the number of items in Select Box
        type = self.browser.find_element_by_id("id_osr_pattern_type")
        options = [x for x in type.find_elements_by_tag_name("option")]

        self.assertEqual(len(options), 5)

        # Match the exact names of the items in select box
        self.assertEqual(options[1].get_attribute("value"), 'Ubiquitous')
        self.assertEqual(options[2].get_attribute("value"), 'Event-Driven')
        self.assertEqual(options[3].get_attribute("value"), 'Unwanted Behavior')
        self.assertEqual(options[4].get_attribute("value"), 'State-Driven')

        # Delete
        btn_delete = self._is_element_not_present(By.XPATH,'//*[@id="report_form"]/div[2]/div[1]/a')
        self.assertEqual(btn_delete, False)

        btn_save = self._is_element_not_present(By.XPATH,'//*[@id="report_form"]/div[2]/div[2]/input[3]')
        self.assertEqual(btn_save, False)

















