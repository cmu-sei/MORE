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
from cwe.cwe_search import CWESearchLocator, CWEKeywordSearch
from cwe.models import *

# Create your tests here.

class CWESearchTest(TestCase):
    """
    This class is the test suite to test the methods of the CWESearchLocator class
    """

    def setUp(self):
        """ Predefined database to set up database
        :param text: None
        :return: None
        """
        self.construct_test_database()
        self.cwe_keyword_search_obj = CWESearchLocator.get_instance()

    def construct_test_database(self):
        """ This function creates the temporary database
        :param text: None
        :return: None
        """
        from cwe.models import Keyword, Category, CWE

        xml = Keyword(name='xml') # 1
        xml.save()

        execut = Keyword(name='execut') # 2
        execut.save()

        remot = Keyword(name='remot') # 3
        remot.save()

        scripting = Keyword(name='scripting') # 4
        scripting.save()

        cross = Keyword(name='cross') # 5
        cross.save()

        upload = Keyword(name='upload') # 6
        upload.save()

        file = Keyword(name='file') # 7
        file.save()

        cod = Keyword(name='cod') # 8
        cod.save()

        javascript = Keyword(name='javascript') # 9
        javascript.save()

        ver = Keyword(name='ver') # 10
        ver.save()

        lack = Keyword(name='lack') # 11
        lack.save()

        valid = Keyword(name='valid') # 12
        valid.save()

        unauth = Keyword(name='unauth') # 13
        unauth.save()

        bypass = Keyword(name='bypass') # 14
        bypass.save()

        auth = Keyword(name='auth') # 15
        auth.save()

        inject = Keyword(name='inject') # 16
        inject.save()

        sql = Keyword(name='sql') # 17
        sql.save()

        cwe = CWE(code=106, name='XML Injection')
        cwe.save()
        cwe.keywords.add(xml)
        cwe.keywords.add(inject)
        cwe.save()

        cwe = CWE(code=105, name='Remote Code Execution')
        cwe.save()
        cwe.keywords.add(execut)
        cwe.keywords.add(remot)
        cwe.keywords.add(cod)
        cwe.save()

        cwe = CWE(code=104, name='Cross site scripting')
        cwe.save()
        cwe.keywords.add(scripting)
        cwe.keywords.add(cross)
        cwe.save()

        cwe = CWE(code=103, name='File Upload Vulnerability')
        cwe.save()
        cwe.keywords.add(upload)
        cwe.keywords.add(file)
        cwe.save()

        cwe = CWE(code=102, name='Code Injection')
        cwe.save()
        cwe.keywords.add(cod)
        cwe.keywords.add(javascript)
        cwe.keywords.add(inject)
        cwe.save()

        cwe = CWE(code=101, name='Authentication bypass')
        cwe.save()
        cwe.keywords.add(ver)
        cwe.keywords.add(lack)
        cwe.keywords.add(valid)
        cwe.keywords.add(unauth)
        cwe.keywords.add(bypass)
        cwe.keywords.add(auth)
        cwe.save()

        cwe = CWE(code=100, name='SQL Injection')
        cwe.save()
        cwe.keywords.add(inject)
        cwe.keywords.add(sql)
        cwe.save()



    def test_registration_with_service_locator(self):
        """
        Note: Here we are combining several test cases in a single method (or test case)
        because django treats each method as a separate test case and it seems that
        it runs test cases in parallel. In this case, the CWEServiceLocator only registers
        a CWESearchBase object if its priority is higher than that of the already registered
        one. So, registering a CWESearchBase object with some priority might fail if a
        CWESearchBase object with the higher priority has already been registered through
        some different test case.
        """

        # Note: Do not register with priority '1' because a default object of CWEKeywordSearch
        # is already registered in the init module (Refer __init__.py).

        # 'register' should successfully register an object of a concrete class of
        # the CWESearchBase and return 'True'
        cwe_keyword_search = CWEKeywordSearch()
        self.assertEqual(CWESearchLocator.register(cwe_keyword_search, 2), True)

        # 'get_cwe_search' should return the object registered with highest priority
        self.assertEqual(CWESearchLocator.get_instance(), cwe_keyword_search)

        # 'register' should successfully register an object of a concrete class of
        # the CWESearchBase with the priority higher than that of the already registered
        # object and return 'True'
        cwe_keyword_search2 = CWEKeywordSearch()
        self.assertEqual(CWESearchLocator.register(cwe_keyword_search2, 3), True)

        # 'register' should not register an object of a concrete class of
        # the CWESearchBase with the priority equal to the priority of the already
        # registered object and return 'False'
        cwe_keyword_search3 = CWEKeywordSearch()
        self.assertEqual(CWESearchLocator.register(cwe_keyword_search3, 3), False)

        # 'register' should not register an object of a concrete class of
        # the CWESearchBase with the priority lower than the priority of the already
        # registered object and return 'False'
        cwe_keyword_search2 = CWEKeywordSearch()
        self.assertEqual(CWESearchLocator.register(cwe_keyword_search2, 1), False)


    def test_registration_with_service_locator_with_instance_not_of_type_CWESearchBase(self):
        """
        'register' should raise a value error when an object that doesn't inherits from
        CWESearchBase tries to register itself.
        """
        self.assertRaises(ValueError, CWESearchLocator.register, 'String Object', 100)



    def test_check_suggestion_sqlinjection(self):
        """ This test case tests the algorithm for SQL Injection
        :param text: None
        :return: None
        """
        # Test # 1: SQL Injection
        text="This module exploits a stacked SQL injection in order to add an administrator user to the " \
                    "SolarWinds Orion database."
        results = self.cwe_keyword_search_obj.search_cwes(text)
        self.assertEqual(results[0][0].name, 'SQL Injection')


    def test_check_suggestion_file_upload_vulnerability(self):
        """ This test case tests the algorithm for File upload vulnerability
        :param text: None
        :return: None
        """
        # Test # 2: File upload vulnerability
        text = "This module exploits a file upload vulnerability in all versions of the Holding Pattern theme found in " \
             "the upload_file.php script which contains no session or file validation. It allows unauthenticated users " \
             "to upload files of any type and subsequently execute PHP scripts in the context of the web server."

        results = self.cwe_keyword_search_obj.search_cwes(text)
        self.assertEqual(results[0][0].name, 'File Upload Vulnerability')

    def test_check_suggestion_cross_site_scripting(self):
        """ This test case tests the algorithm for Cross site scripting
        :param text: None
        :return: None
        """
        # Test # 3: Cross site scripting
        text = "This module exploits a universal cross-site scripting (UXSS) vulnerability found in Internet Explorer " \
               "10 and 11. By default, you will steal the cookie from TARGET_URI (which cannot have X-Frame-Options or " \
               "it will fail). You can also have your own custom JavaScript by setting the CUSTOMJS option. Lastly, " \
               "you might need to configure the URIHOST option if you are behind NAT."
        results = self.cwe_keyword_search_obj.search_cwes(text)
        self.assertEqual(results[0][0].name, 'Cross site scripting')

    def test_check_suggestion_blank_text(self):
        """ This test case tests the algorithm for Blank text
        :param text: None
        :return: None
        """
        # Test # 4: Blank text
        text=""
        results = self.cwe_keyword_search_obj.search_cwes(text)
        self.assertEqual(len(results), 0)

    def test_check_suggestion_sql_injection_not_exists(self):
        """ This test case tests the algorithm for 'SQL Injection' does not exist in the description
        :param text: None
        :return: None
        """
        # Test # 5: 'SQL Injection' does not exist in the description
        text="This module exploits a hidden backdoor API in Apple's Admin framework on Mac OS X to escalate privileges " \
             "to root, dubbed \"Rootpipe.\" This module was tested on Yosemite 10.10.2 and should work on previous versions. " \
             "The patch for this issue was not backported to older releases. Note: you must run this exploit as an " \
             "admin user to escalate to root."
        results = self.cwe_keyword_search_obj.search_cwes(text)
        res = False
        if len([cwe for cwe, count in results if 'SQL Injection' in cwe.name]) > 0:
            res=True
        self.assertEqual(res, False)

    def test_check_suggestion_integers_as_string(self):
        """ This test case tests the algorithm for All Integers
        :param text: None
        :return: None
        """
        # Test # 6: All Integers
        text="111111111111111122222222222222223333333333333444444444"
        results = self.cwe_keyword_search_obj.search_cwes(text)

        self.assertEqual(len(results), 0)

    def test_check_suggestion_text_none(self):
        """ This test case tests the algorithm for File upload vulnerability
        :param text: None
        :return: None
        """
        # Test # 7: None
        text = None
        results = self.cwe_keyword_search_obj.search_cwes(text)
        self.assertEqual(not results, True)

    def test_check_suggestion_text_false(self):
        """ This test case tests the algorithm for File upload vulnerability
        :param text: None
        :return: None
        """
        # Test # 7: False
        text = False
        results = self.cwe_keyword_search_obj.search_cwes(text)
        self.assertEqual(not results, True)

    def test_check_suggestion_integers(self):
        """ This test case tests the algorithm for All Integers
        :param text: None
        :return: None
        """
        # Test # 6: All Integers
        text=111111111111111111
        res = False
        try:
            results = self.cwe_keyword_search_obj.search_cwes(text)
        except ValueError:
            res = True # It means value error exception really occurred

        self.assertEqual(res, True)


    def test_check_suggestion_sqlinjection_uppercase(self):
        """ This test case tests the algorithm for SQL Injection
        :param text: None
        :return: None
        """
        # Test # 1: SQL Injection
        text="This module exploits a stacked SQL injection in order to add an administrator user to the " \
                    "SolarWinds Orion database."
        results_lowercase = self.cwe_keyword_search_obj.search_cwes(text)
        results_uppercase = self.cwe_keyword_search_obj.search_cwes(text.upper())
        self.assertEqual(len(results_lowercase), len(results_uppercase))
        self.assertEqual(results_lowercase[0][0].name, results_uppercase[0][0].name)
        self.assertEqual(results_lowercase[1][0].name, results_uppercase[1][0].name)
        self.assertEqual(results_lowercase[2][0].name, results_uppercase[2][0].name)



    def test_remove_non_alphanumeric_characters(self):
        """ This test case tests the algorithm that it removes non-alphanumeric characters except underscores
        :param text: None
        :return: None
        """
        text = "underscores_are allowed. However, hyphen-are not allowed!"
        expected = ['underscores_are', 'allowed', 'however', 'hyphen', 'allowed']
        result = self.cwe_keyword_search_obj.remove_stopwords(text)
        self.assertEqual(result, expected)


        text = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
        expected = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz0123456789_"
        result = self.cwe_keyword_search_obj.remove_stopwords(text)[0]
        self.assertEqual(result, expected)



    def test_suggested_keywords_sorted_by_frequency(self):
        """ This test case tests the algorithm that it returns suggested keywords sorted by the frequency in the text
        :param text: None
        :return: None
        """
        text = "client client bypass authentication authent authentication"
        expected = ['authent', 'client', 'bypass']

        filtered_words = self.cwe_keyword_search_obj.remove_stopwords(text)
        keywords = self.cwe_keyword_search_obj.stem_text(filtered_words)

        self.assertEqual(keywords, expected)
