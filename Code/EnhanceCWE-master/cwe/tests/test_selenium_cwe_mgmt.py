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
from EnhancedCWE.settings_travis import SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT
from register.tests import RegisterHelper
from cwe.models import Keyword
from cwe.models import Category
from cwe.models import CWE

class CWEManagement(StaticLiveServerTestCase):

    # The URLs of the CWE-related pages.
    PAGE_URL_CWE_HOME = "/app/cwe/cwe/"
    PAGE_URL_CWE_ADD = "/app/cwe/cwe/add/"

    def setUp(self):
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
        # Call tearDown to close the web browser
        self.browser.quit()
        # Call the tearDown() of parent class.
        super(CWEManagement, self).tearDown()

    def _open_page_cwe_home(self):
        """
        Open the "CWEs" page.
        """
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_CWE_HOME))

    def _open_page_cwe_add(self):
        """
        Open the "Add CWE" page.
        """
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_URL_CWE_ADD))

    def test_point_01_ui_verification(self):
        """
        Test Point: Verify that the "Add CWE" UI elements are correctly displayed.
        """
        self._open_page_cwe_add()
        # 'Code' has an asterisk.
        label_code_asterisk = self.browser.find_element_by_xpath('//label[@for="id_code"]/span')
        self.assertEqual(label_code_asterisk.get_attribute("textContent"), "*")
        # 'Name' has an asterisk.
        label_name_asterisk = self.browser.find_element_by_xpath('//label[@for="id_name"]/span')
        self.assertEqual(label_name_asterisk.get_attribute("textContent"), "*")
        # 'Categories' has an asterisk.
        label_categories_asterisk = self.browser.find_element_by_xpath('//label[@for="id_categories"]/span')
        self.assertEqual(label_categories_asterisk.get_attribute("textContent"), "*")

    def test_point_02_add_cwe_error_msg_shown_correctly(self):
        """
        Test Point: Verify that error messages are shown correctly when fields are not correctly filled.
        Error messages include:
            - A "Please correct the errors below" message is shown.
            - 'Code' is not filled in.
            - 'Code' is not an integer.
            - 'Name' is not filled in.
            - 'Categories' is not specified.
        """
        self._open_page_cwe_add()
        # Do not enter anything but directly click "Save" button.
        # Click Button: "Save"
        self.browser.find_element_by_name("_save").click()

        # Verify: The error messages are shown.
        err_msg = self.browser.find_element_by_xpath("//div[@class='alert alert-danger']").get_attribute("textContent")
        self.assertEqual(err_msg.strip(), "Please correct the errors below.")
        # Verify: 'Code': "This field is required" is shown.
        label_err_msg_code = self.browser.find_element_by_xpath("//p[@id='error_1_id_code']/strong")
        self.assertEqual(label_err_msg_code.get_attribute("textContent"), "This field is required.")
        # Verify: 'Name': "This field is required" is shown.
        label_err_msg_name = self.browser.find_element_by_xpath("//p[@id='error_1_id_name']/strong")
        self.assertEqual(label_err_msg_name.get_attribute("textContent"), "This field is required.")
        # Verify: 'Categories': "This field is required" is shown.
        label_err_msg_categories = self.browser.find_element_by_xpath("//p[@id='error_1_id_categories']/strong")
        self.assertEqual(label_err_msg_categories.get_attribute("textContent"), "This field is required.")

        # Enter Text: "Code": "abc"
        self.browser.find_element_by_id("id_code").send_keys("abc")
        # Click Button: "Save"
        self.browser.find_element_by_name("_save").click()
        # Enter Text: "Code": "1234.5"
        self.browser.find_element_by_id("id_code").send_keys("1234.5")
        # Click Button: "Save"
        self.browser.find_element_by_name("_save").click()

        # Verify: 'Code': Error message is shown.
        label_err_msg_code = self.browser.find_element_by_xpath("//p[@id='error_1_id_code']/strong")
        self.assertEqual(label_err_msg_code.get_attribute("textContent"), "Enter a whole number.")

    def test_point_03_keyword_suggestion_works_correctly(self):

        # Create a CWE.
        kw1 = Keyword(name="bypass")
        kw1.save()
        cat_1 = Category(name="category_1")
        cat_1.save()
        cwe_obj = CWE(code=1234, name="cwe_1")
        cwe_obj.save()
        cwe_obj.keywords.add(kw1)
        cwe_obj.categories.add(cat_1)

        # Open the created CWE.
        self.browser.get("%s%s%s/" % (self.live_server_url, "/app/cwe/cwe/", str(cwe_obj.id)))

        # Verify: "Get Keywords Suggestions" area is shown.
        elm_title_keyword_suggestions = self.browser.find_elements_by_xpath("//h3")[3]
        self.assertEqual(elm_title_keyword_suggestions.get_attribute("textContent").strip(), "Get Keywords Suggestions")

        # Enter Text: "Suggest Text Area": "This is a CWE about authentication bypass"
        self.browser.find_element_by_id("suggest_textarea").send_keys("This is a CWE about authentication bypass")
        # Click Button: "Request Suggestions"
        self.browser.find_element_by_id("suggest_button").click()

        # Verify: Suggested keywords are listed.
        self.assertTrue(self.browser.find_elements_by_xpath("//span[@data-value='cwe']") is not None)
        self.assertTrue(self.browser.find_elements_by_xpath("//span[@data-value='bypass']") is not None)
        self.assertTrue(self.browser.find_elements_by_xpath("//span[@data-value='authent']") is not None)

        # Click Button: "Add Keywords"
        self.browser.find_element_by_id("add_keywords_button").click()

        # Verify: Keywords are added.
        added_keywords = self.browser.find_elements_by_xpath("//span[@id='id_keywords-deck']/span")
        # Only three keywords, which means we do not add "bypass" again because it's already there.
        self.assertEqual(len(added_keywords), 3)
        # Because the "textContent" contains a non-ASCII character, we need to hold it in Unicode.
        self.assertTrue(unicode(added_keywords[0].get_attribute("textContent")).rfind("bypass") != -1)
        self.assertTrue(unicode(added_keywords[1].get_attribute("textContent")).rfind("cwe") != -1)
        self.assertTrue(unicode(added_keywords[2].get_attribute("textContent")).rfind("authent") != -1)

        # Click Button: "Save"
        self.browser.find_element_by_name("_save").click()

        # Verify: The new keywords are added successfully.
        keywords = cwe_obj.keywords
        self.assertEqual(keywords.count(), 3)
        self.assertTrue(keywords.get(name="bypass") is not None)
        self.assertTrue(keywords.get(name="cwe") is not None)
        self.assertTrue(keywords.get(name="authent") is not None)
