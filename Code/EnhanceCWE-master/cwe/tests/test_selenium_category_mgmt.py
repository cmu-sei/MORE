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
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse
from selenium import webdriver
from register.tests import RegisterHelper
from EnhancedCWE.settings_travis import SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT
from cwe.models import Category
from cwe.models import CWE


CATEGORY_NAME_MAX_LENGTH = 128


class CategoryManagement(LiveServerTestCase):

    # The URL of the "Category" page.
    PAGE_CATEGORY_URL = "/app/cwe/category/"
    # The title of the "Category" page.
    PAGE_CATEGORY_TITLE = u"Select Category to change | Admin Area"

    # A very long name for category.
    CATEGORY_TOO_LONG_NAME = "123456789_123456789_123456789_123456789_123456789_" \
                             "123456789_123456789_123456789_123456789_123456789_" \
                             "123456789_123456789_123456789_123456789_"

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
        super(CategoryManagement, self).tearDown()

    # Helper methods

    def _open_page_categories(self):
        """
        Open the "Categories" page.
        """
        self.browser.get("%s%s" % (self.live_server_url, self.PAGE_CATEGORY_URL))

    def _add_cwe_referring_to_category_1(self):
        """
        Create a CWE that refers to "category_1"
        """
        category_1 = Category.objects.get(name="category_1")

        cwe = CWE(code=1, name="cwe_1")
        cwe.save()
        cwe.categories.add(category_1)

    # Test cases

    def _test_point_01_category_can_be_added(self):
        # Click Button: "Add Category"
        self.browser.find_element_by_link_text("Add Category").click()
        # Enter Text: "category_1"
        self.browser.find_element_by_id("id_name").send_keys("category_1")
        # Click Button: "Save and add another"
        self.browser.find_element_by_name("_addanother").click()
        # Enter Text: "category"
        self.browser.find_element_by_id("id_name").send_keys("category")
        # Click Button: "Save and continue editing"
        self.browser.find_element_by_name("_continue").click()
        # Enter Text: "_2" (to complete the category name)
        self.browser.find_element_by_id("id_name").send_keys("_2")
        # Click Button: "Save"
        self.browser.find_element_by_name("_save").click()

        # Verify: Two categories have been added.
        elm_category_1 = self.browser.find_element_by_link_text("category_1")
        elm_category_2 = self.browser.find_element_by_link_text("category_2")
        self.assertTrue(elm_category_1 is not None)
        self.assertTrue(elm_category_2 is not None)
        # Verify: ONLY two categories have been added.
        table_rows = self.browser.find_elements_by_xpath('//table[@id="result_list"]/tbody/tr')
        self.assertEqual(len(table_rows), 2)

    def _test_point_02_too_long_name_can_be_cut(self):
        # Click Button: "Add Category"
        self.browser.find_element_by_link_text("Add Category").click()
        # Enter Text: CATEGORY_TOO_LONG_NAME
        self.browser.find_element_by_id("id_name").send_keys(self.CATEGORY_TOO_LONG_NAME)

        # Verify: "Name" only contains CATEGORY_TOO_LONG_NAME[0:CATEGORY_NAME_MAX_LENGTH]
        category_name_actual = self.browser.find_element_by_id("id_name").get_attribute("value")
        self.assertEqual(category_name_actual, self.CATEGORY_TOO_LONG_NAME[0:CATEGORY_NAME_MAX_LENGTH])

        # Click Button: "Save"
        self.browser.find_element_by_name("_save").click()

        # Verify: A category named CATEGORY_TOO_LONG_NAME[0:CATEGORY_NAME_MAX_LENGTH]
        elm_category_too_long_name = self.browser.find_element_by_link_text(
            self.CATEGORY_TOO_LONG_NAME[0:CATEGORY_NAME_MAX_LENGTH]
        )
        self.assertTrue(elm_category_too_long_name is not None)

    def _test_point_03_category_info_can_be_viewed(self):
        # Click Link: "category_1"
        self.browser.find_element_by_link_text("category_1").click()

        # Verify: "Name" has text "category_1"
        category_name_displayed = self.browser.find_element_by_id("id_name").get_attribute("value")
        self.assertEqual(category_name_displayed, "category_1")

        # Go Backward: 1 step
        self.browser.back()
        # Click Link: CATEGORY_TOO_LONG_NAME[0:CATEGORY_NAME_MAX_LENGTH]
        self.browser.find_element_by_link_text(self.CATEGORY_TOO_LONG_NAME[0:CATEGORY_NAME_MAX_LENGTH]).click()

        # Verify: "Name" has text CATEGORY_TOO_LONG_NAME[0:CATEGORY_NAME_MAX_LENGTH]
        category_name_displayed = self.browser.find_element_by_id("id_name").get_attribute("value")
        self.assertEqual(category_name_displayed, self.CATEGORY_TOO_LONG_NAME[0:CATEGORY_NAME_MAX_LENGTH])

    def _test_point_04_category_info_can_be_updated(self):
        # Click Link: CATEGORY_TOO_LONG_NAME[0:CATEGORY_NAME_MAX_LENGTH]
        self.browser.find_element_by_link_text(self.CATEGORY_TOO_LONG_NAME[0:CATEGORY_NAME_MAX_LENGTH]).click()
        # Clear Text: "Name"
        self.browser.find_element_by_id("id_name").clear()
        # Enter Text: "category_3"
        self.browser.find_element_by_id("id_name").send_keys("category_3")
        # Click Button: "Save"
        self.browser.find_element_by_name("_save").click()

        # Verify: Now there are three categories.
        elm_category_1 = self.browser.find_element_by_link_text("category_1")
        elm_category_2 = self.browser.find_element_by_link_text("category_2")
        elm_category_3 = self.browser.find_element_by_link_text("category_3")
        self.assertTrue(elm_category_1 is not None)
        self.assertTrue(elm_category_2 is not None)
        self.assertTrue(elm_category_3 is not None)
        # Verify: ONLY three categories have been added. In other words, the
        # category CATEGORY_TOO_LONG_NAME[0:CATEGORY_NAME_MAX_LENGTH] no longer exists.
        table_rows = self.browser.find_elements_by_xpath('//table[@id="result_list"]/tbody/tr')
        self.assertEqual(len(table_rows), 3)

    def _test_point_05_category_cannot_be_deleted_when_referred_to(self):
        # Create a CWE that refers to "category_1".
        self._add_cwe_referring_to_category_1()
        # Click Link: "category_1"
        self.browser.find_element_by_link_text("category_1").click()
        # Click Button: "Delete"
        self.browser.find_element_by_link_text("Delete").click()
        # Click Button: "Yes, I'm sure"
        self.browser.find_element_by_xpath('id("content")/form/div/input[2]').click()

        # Verify: An alert message is shown to say the deletion fails.
        alert_msg_expected = "The Category \"category_1\" cannot be deleted as there are CWEs referring to it!"
        alert_msg_actual = self.browser.find_element_by_xpath(
            'id("content")/div/div/div'
        ).get_attribute("textContent").strip()
        self.assertEqual(alert_msg_actual, alert_msg_expected)
        # Verify: "category_1" is not deleted.
        elm_category_1 = self.browser.find_element_by_link_text("category_1")
        self.assertTrue(elm_category_1 is not None)

    def _test_point_06_category_can_be_deleted_after_reference_removed(self):
        # Click Link: "category_2"
        self.browser.find_element_by_link_text("category_2").click()
        # Click Button: "Delete"
        self.browser.find_element_by_link_text("Delete").click()
        # Click Button: "Yes, I'm sure"
        self.browser.find_element_by_xpath('id("content")/form/div/input[2]').click()

        # Verify: Now there are only two categories remaining.
        elm_category_1 = self.browser.find_element_by_link_text("category_1")
        elm_category_3 = self.browser.find_element_by_link_text("category_3")
        self.assertTrue(elm_category_1 is not None)
        self.assertTrue(elm_category_3 is not None)
        # Verify: ONLY two categories remain. In other words, "category_2" no longer exists.
        table_rows = self.browser.find_elements_by_xpath('//table[@id="result_list"]/tbody/tr')
        self.assertEqual(len(table_rows), 2)

    def _test_point_07_category_can_be_deleted_if_no_reference(self):
        # Delete the CWE.
        CWE.objects.all().delete()
        # Click Link: "category_1"
        self.browser.find_element_by_link_text("category_1").click()
        # Click Button: "Delete"
        self.browser.find_element_by_link_text("Delete").click()
        # Click Button: "Yes, I'm sure"
        self.browser.find_element_by_xpath('id("content")/form/div/input[2]').click()

        # Verify: Now there is only "category_3" remaining.
        elm_category_3 = self.browser.find_element_by_link_text("category_3")
        self.assertTrue(elm_category_3 is not None)
        # Verify: ONLY one category remains. In other words, "category_1" no longer exists.
        table_rows = self.browser.find_elements_by_xpath('//table[@id="result_list"]/tbody/tr')
        self.assertEqual(len(table_rows), 1)

    def test_category_management(self):
        self._open_page_categories()
        self._test_point_01_category_can_be_added()
        self._open_page_categories()
        self._test_point_02_too_long_name_can_be_cut()
        self._open_page_categories()
        self._test_point_03_category_info_can_be_viewed()
        self._open_page_categories()
        self._test_point_04_category_info_can_be_updated()
        self._open_page_categories()
        self._test_point_05_category_cannot_be_deleted_when_referred_to()
        self._open_page_categories()
        self._test_point_06_category_can_be_deleted_after_reference_removed()
        self._open_page_categories()
        self._test_point_07_category_can_be_deleted_if_no_reference()
