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
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException
from EnhancedCWE.settings_travis import SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT
from cwe.models import Category
from cwe.models import Keyword
from cwe.models import CWE
from register.tests import RegisterHelper


KEYWORD_NAME_MAX_LENGTH = 32


class KeywordManagement(LiveServerTestCase):

    def setUp(self):
        # Create the admin.
        RegisterHelper.create_superuser()

        # Launch a browser.
        self.browser = webdriver.Firefox()

        # Log in.
        RegisterHelper.fill_login_form(
            selenium=self.browser,
            login_url="%s%s" % (self.live_server_url, reverse("account_login")),
            admin=True
        )
        RegisterHelper.submit_login_form(selenium=self.browser)

        # Call the setUp() of parent class.
        super(KeywordManagement, self).setUp()

    def tearDown(self):
        # Call tearDown to close the web browser
        self.browser.quit()

        # Call the tearDown() of parent class.
        super(KeywordManagement, self).tearDown()

    def _br_go_to(self, url):
        self.browser.get('%s%s' % (self.live_server_url, url))

    def _br_go_backward(self, steps=1):
        for i in range(0, steps):
            self.browser.back()

    def _br_go_forward(self, steps=1):
        for i in range(0, steps):
            self.browser.forward()

    def _br_find_element(self, by, locator, timeout=SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT):
        return WebDriverWait(self.browser, timeout).until(
            expected_conditions.presence_of_element_located((by, locator))
        )

    def _br_find_element_or_none(self, by, locator, timeout=SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT):
        try:
            return self._br_find_element(by, locator, timeout)
        except TimeoutException:
            return None

    def _br_find_elements(self, by, locator, timeout=SELENIUM_WEB_ELEMENT_PRESENCE_CHECK_TIMEOUT):
        return WebDriverWait(self.browser, timeout).until(
            expected_conditions.presence_of_all_elements_located((by, locator))
        )

    def _br_click(self, by, locator):
        elm = self._br_find_element(by, locator)
        elm.click()
        return elm

    def _br_send_keys(self, by, locator, keys):
        elm = self._br_find_element(by, locator)
        elm.send_keys(keys)
        return elm

    def _br_retrieve_text(self, by, locator):
        elm = self._br_find_element(by, locator)
        return elm.get_attribute("value")

    def _br_clear_text(self, by, locator):
        elm = self._br_find_element(by, locator)
        elm.clear()

    def _br_select_option_text(self, by, locator, option_text):
        elm = self._br_find_element(by, locator)
        sel = Select(webelement=elm)
        sel.select_by_visible_text(option_text)
        return elm

    def _db_op__cwe__add(self):
        cat = Category(name="category_1")
        cat.save()

        kw1 = Keyword.objects.get(name="keyword_1")

        cwe = CWE(code=1, name="cwe_name")
        cwe.save()
        cwe.categories.add(cat)
        cwe.keywords.add(kw1)

        self.assertEqual(CWE.objects.all().count(), 1)

    def _tp_positive_keyword_adding_can_be_successful(self):
        # Assert Page: "Keywords"

        # Verify: There are two keywords: keyword_1, keyword_2.
        elm_keyword_1 = self._br_find_element(By.LINK_TEXT, "keyword_1")
        elm_keyword_2 = self._br_find_element(By.LINK_TEXT, "keyword_2")
        self.assertIsNot(elm_keyword_1, None)
        self.assertIsNot(elm_keyword_2, None)

        # Verify: There are only two keywords.
        table_rows = self._br_find_elements(By.XPATH, '//table[@id="result_list"]/tbody/tr')
        self.assertEqual(len(table_rows), 2)

    def _tp_negative_too_long_keyword_name_is_cut(self, keyword_name_too_long):
        # Verify: Only the first `KEYWORD_NAME_MAX_LENGTH` characters are kept.
        keyword_name_actual = self._br_retrieve_text(By.ID, "id_name")
        self.assertEqual(keyword_name_actual, keyword_name_too_long[:KEYWORD_NAME_MAX_LENGTH])

    def _tp_positive_keyword_with_long_name_can_be_added(self, keyword_name_too_long):
        # Verify: There are three keywords: keyword_1, keyword_2, keyword_name_too_long[:KEYWORD_NAME_MAX_LENGTH]
        elm_keyword_1 = self._br_find_element(By.LINK_TEXT, "keyword_1")
        elm_keyword_2 = self._br_find_element(By.LINK_TEXT, "keyword_2")
        elm_keyword_long_name = self._br_find_element(By.LINK_TEXT, keyword_name_too_long[:KEYWORD_NAME_MAX_LENGTH])
        self.assertIsNot(elm_keyword_1, None)
        self.assertIsNot(elm_keyword_2, None)
        self.assertIsNot(elm_keyword_long_name, None)

    def _tp_positive_keyword_info_can_be_viewed(self, expected_keyword_name):
        # Verify: The keyword name is displayed in the text box.
        keyword_name_actual = self._br_retrieve_text(By.ID, "id_name")
        self.assertEqual(keyword_name_actual, expected_keyword_name)

    def _tp_positive_keyword_info_can_be_changed(self, original_keyword_name):
        # Verify: The keyword name is changed to "keyword_3"
        # 1). Verify that the old keyword entry is gone.
        elm_keyword_long_name = self._br_find_element_or_none(By.LINK_TEXT, original_keyword_name, timeout=3)
        self.assertIsNone(elm_keyword_long_name)
        # 2). Verify that "keyword_3" is in.
        elm_keyword_3 = self._br_find_element(By.LINK_TEXT, "keyword_3")
        self.assertIsNot(elm_keyword_3, None)

    def _tp_positive_keyword_can_be_deleted(self, keyword_name):
        # Verify: "keyword_1" has been deleted.
        elm_keyword = self._br_find_element_or_none(By.LINK_TEXT, keyword_name, timeout=3)
        self.assertIsNone(elm_keyword)

    def test_keyword_management(self):
        # Assert Page: Admin Home.

        # ==================================================
        # Open Page: "Keywords"
        self._br_click(By.LINK_TEXT, "Keywords")
        # Open Page: "Add Keyword"
        self._br_click(By.LINK_TEXT, "Add Keyword")
        # Assert Page: "Add Keyword"
        # Enter a valid keyword name.
        self._br_send_keys(By.ID, "id_name", "keyword_1")
        # Click Button: "Save and add another"
        self._br_click(By.NAME, "_addanother")
        # Enter another valid keyword name.
        self._br_send_keys(By.ID, "id_name", "keyword_2")
        # Click Button: "Save"
        self._br_click(By.NAME, "_save")

        # Test Point: Adding keywords can be successful.
        self._tp_positive_keyword_adding_can_be_successful()

        # ==================================================
        # Open Page: "Add Keyword"
        self._br_click(By.LINK_TEXT, "Add Keyword")
        # Assert Page: "Add Keyword"
        # Try to enter a keyword name that is too long.
        keyword_name_too_long = "keyword_name_should_not_be_more_than_32_characters_but_this_name_is_too_long"
        self._br_send_keys(By.ID, "id_name", keyword_name_too_long)

        # Test Point: Keyword length is limited correctly.
        self._tp_negative_too_long_keyword_name_is_cut(keyword_name_too_long)

        # ==================================================
        # Click Button: "Save"
        self._br_click(By.NAME, "_save")

        # Test Point: Keyword with long name can be saved successfully.
        self._tp_positive_keyword_with_long_name_can_be_added(keyword_name_too_long)

        # ==================================================
        # Click Link: "keyword_1"
        self._br_click(By.LINK_TEXT, "keyword_1")

        # Test Point: Keyword information can be viewed correctly.
        self._tp_positive_keyword_info_can_be_viewed("keyword_1")

        # Backward: "Keywords" page
        self._br_go_backward()
        # Click Link: "keyword_2"
        self._br_click(By.LINK_TEXT, "keyword_2")

        # Test Point: Keyword information can be viewed correctly.
        self._tp_positive_keyword_info_can_be_viewed("keyword_2")

        # Backward: "Keywords" page
        self._br_go_backward()
        # Click Link: keyword_name_too_long[:KEYWORD_NAME_MAX_LENGTH]
        self._br_click(By.LINK_TEXT, keyword_name_too_long[:KEYWORD_NAME_MAX_LENGTH])

        # Test Point: Keyword information can be viewed correctly.
        self._tp_positive_keyword_info_can_be_viewed(keyword_name_too_long[:KEYWORD_NAME_MAX_LENGTH])

        # ==================================================
        # Change the too long keyword name to "keyword_3".
        self._br_clear_text(By.ID, "id_name")
        self._br_send_keys(By.ID, "id_name", "keyword_3")
        # Click Button: "Save"
        self._br_click(By.NAME, "_save")

        # Test Point
        self._tp_positive_keyword_info_can_be_changed(keyword_name_too_long[:KEYWORD_NAME_MAX_LENGTH])

        # ==================================================
        # Open Page: Admin Home.
        self._br_go_to("/app/")
        # Add a CWE
        self._db_op__cwe__add()
        # Open Page: "Keywords"
        self._br_click(By.LINK_TEXT, "Keywords")
        # Click Link: "keyword_1"
        self._br_click(By.LINK_TEXT, "keyword_1")
        # Click Button: "Delete"
        self._br_click(By.LINK_TEXT, "Delete")
        # Click Button: "Yes, I'm sure"
        self._br_click(By.XPATH, 'id("content")/form/div/input[2]')

        # Test Point: Keyword can be deleted.
        self._tp_positive_keyword_can_be_deleted("keyword_1")

        # ==================================================
        # Assert Page: "Keywords"
        # Click Checkbox: All keywords
        # Simply clicking on the toggle checkbox seems not to work... So I have click each.
        # self._br_click(By.ID, "action-toggle")
        checkboxes = self._br_find_elements(By.NAME, "_selected_action")
        for chk in checkboxes:
            chk.click()
        # Select Option: "Delete selected keywords"
        self._br_select_option_text(By.TAG_NAME, "select", "Delete selected Keywords")
        # Click Button: "Go"
        self._br_click(By.XPATH, '//button[@type="submit"][contains(text(), "Go")]')
        # Click Button: "Yes, I'm sure"
        self._br_click(By.XPATH, 'id("content")/form/div/div/div/input')

        # Verify: All keywords are deleted.
        self._tp_positive_keyword_can_be_deleted("keyword_1")
        self._tp_positive_keyword_can_be_deleted("keyword_2")
        self._tp_positive_keyword_can_be_deleted(keyword_name_too_long[:KEYWORD_NAME_MAX_LENGTH])
