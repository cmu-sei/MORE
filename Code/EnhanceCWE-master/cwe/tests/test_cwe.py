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
from django.db import transaction, IntegrityError
from cwe.models import Category
from cwe.models import Keyword
from cwe.models import CWE
from django.contrib import admin
from cwe.admin import CWEAdmin


class TestSearchCWE(TestCase):

    KEYWORD_NAMES = ["authentication", "file"]
    STEMMED_NAMES = ["authent", "file"]
    CATEGORY_NAMES = ["Web Problems", "Error Handling"]

    def construct_test_database(self):
        # Create the first keyword
        kw1 = Keyword(name=self.KEYWORD_NAMES[0])
        kw1.save()
        # Create the second keyword
        kw2 = Keyword(name=self.KEYWORD_NAMES[1])
        kw2.save()

        # Create the first category
        cat1 = Category(name=self.CATEGORY_NAMES[0])
        cat1.save()
        # Create the second category
        cat2 = Category(name=self.CATEGORY_NAMES[1])
        cat2.save()

        # Create multiple CWEs to test multiplicity.
        # Create CWE with (kw1, cat1)
        cwe1 = CWE(code=101, name="cwe-101", description="")
        cwe1.save()
        cwe1.keywords.add(kw1)
        cwe1.categories.add(cat1)

        # Create CWE with (kw1, cat2)
        cwe2 = CWE(code=102, name="cwe-102", description="")
        cwe2.save()
        cwe2.keywords.add(kw1)
        cwe2.categories.add(cat2)

        # Create CWE with (kw2, cat1)
        cwe3 = CWE(code=103, name="cwe-103", description="")
        cwe3.save()
        cwe3.keywords.add(kw2)
        cwe3.categories.add(cat1)

        # Create CWE with (kw2, cat2)
        cwe4 = CWE(code=104, name="cwe-104", description="")
        cwe4.save()
        cwe4.keywords.add(kw2)
        cwe4.categories.add(cat2)

    def destruct_test_database(self):

        # First we need to delete all the CWEs in order to delete other stuff.
        CWE.objects.all().delete()

        # Then we can delete keywords and categories.
        Keyword.objects.all().delete()
        Category.objects.all().delete()

    def test_positive_cwe_model_admin(self):
        # Verify that the model's admin class has specified the name, keyword and category as
        # parts of the search criteria.
        admin_obj = CWEAdmin(model=CWE, admin_site=admin.site)
        self.assertEqual('name' in admin_obj.search_fields, True)
        self.assertEqual('categories__name' in admin_obj.search_fields, True)
        self.assertEqual('keywords__name' in admin_obj.search_fields, True)


class TestAddCWE(TestCase):

    KEYWORD_NAMES = ["authentication", "file"]
    STEMMED_NAMES = ["authent", "file"]
    CATEGORY_NAMES = ["Web Problems", "Error Handling"]

    def setUp(self):
        self.construct_test_database()

    def tearDown(self):
        self.destruct_test_database()

    def construct_test_database(self):
        # Create the first keyword
        kw1 = Keyword(name=self.KEYWORD_NAMES[0])
        kw1.save()
        # Create the second keyword
        kw2 = Keyword(name=self.KEYWORD_NAMES[1])
        kw2.save()

        # Create the first category
        cat1 = Category(name=self.CATEGORY_NAMES[0])
        cat1.save()
        # Create the second category
        cat2 = Category(name=self.CATEGORY_NAMES[1])
        cat2.save()

    def destruct_test_database(self):

        # Delete all the CWEs that we added during the test.
        # Otherwise we cannot delete the keywords and categories.
        CWE.objects.all().delete()

        # Then we can delete keywords and categories.
        Keyword.objects.all().delete()
        Category.objects.all().delete()

    def test_positive_single_category_single_keyword(self):

        # First, make sure that the CWE does not exist.
        self.assertRaises(CWE.DoesNotExist, CWE.objects.get, code=101)

        # Second, try to add the CWE to the database.
        cat1 = Category.objects.get(name=self.CATEGORY_NAMES[0])
        kw1 = Keyword.objects.get(name=self.STEMMED_NAMES[0])
        cwe = CWE(code=101, name="cwe-101", description="cwe description")
        cwe.save()
        cwe.categories.add(cat1)
        cwe.keywords.add(kw1)

        # Third, verify that the CWE was added successfully.
        cwe2 = CWE.objects.get(code=101)
        self.assertEqual(cwe.code, cwe2.code)
        self.assertEqual(cwe.name, cwe2.name)
        self.assertEqual(cwe.description, cwe2.description)
        self.assertEqual(cwe.categories.count(), 1)
        self.assertEqual(cwe.keywords.count(), 1)
        self.assertEqual(cwe.categories.first(), cat1)
        self.assertEqual(cwe.keywords.first(), kw1)

    def test_positive_multi_categories_multi_keywords(self):

        # First, make sure that the CWE does not exist.
        self.assertRaises(CWE.DoesNotExist, CWE.objects.get, code=101)

        # Second, try to add the CWE to the database
        cat1 = Category.objects.get(name=self.CATEGORY_NAMES[0])
        kw1 = Keyword.objects.get(name=self.STEMMED_NAMES[0])
        cat2 = Category.objects.get(name=self.CATEGORY_NAMES[1])
        kw2 = Keyword.objects.get(name=self.STEMMED_NAMES[1])
        cwe = CWE(code=101, name="cwe-101", description="cwe description")
        cwe.save()
        cwe.categories.add(cat1, cat2)
        cwe.keywords.add(kw1, kw2)

        # Third, verify that the CWE was added successfully.
        cwe2 = CWE.objects.get(code=101)
        self.assertEqual(cwe.code, cwe2.code)
        self.assertEqual(cwe.name, cwe2.name)
        self.assertEqual(cwe.description, cwe2.description)
        self.assertEqual(cwe.categories.count(), 2)
        self.assertEqual(cwe.keywords.count(), 2)
        self.assertEqual(cwe.categories.get(name=self.CATEGORY_NAMES[0]), cat1)
        self.assertEqual(cwe.categories.get(name=self.CATEGORY_NAMES[1]), cat2)
        self.assertEqual(cwe.keywords.get(name=self.STEMMED_NAMES[0]), kw1)
        self.assertEqual(cwe.keywords.get(name=self.STEMMED_NAMES[1]), kw2)

    def test_negative_add_duplicated(self):

        # First, make sure that the CWE does not exist.
        self.assertRaises(CWE.DoesNotExist, CWE.objects.get, code=105)

        # Second, add the CWE to the database, and it should succeed.
        # Because we want to test the prevention of duplication, we can ignore the
        # CWE category and keyword for now and focus on the CWE code.
        cwe = CWE(code=105, name="cwe-105", description="cwe description")
        cwe.save()
        cwe2 = CWE.objects.get(code=105)
        self.assertEqual(cwe.code, cwe2.code)

        # Thrid, try to add a CWE with the same code, and an exception should
        # be thrown.
        cwe_dup = CWE(code=105, name="cwe-duplicated", description="cwe duplicated description")
        # In Django 1.5/1.6, each test is wrapped in a transaction, so if an exception occurs,
        # it breaks the transaction until you explicitly roll it back. Therefore, any further
        # ORM operations in that transaction, will fail with that django.db.transaction.TransactionManagementError
        # exception. We need to capture the exception with transaction.atomic().
        # See the Django document: https://docs.djangoproject.com/en/1.8/topics/db/transactions/
        with transaction.atomic():
            self.assertRaises(IntegrityError, cwe_dup.save)

    # TODO: The test case below is commented out temporarily because it does not pass. We need to fix it later.
    #
    # # A CWE cannot be created without name
    # # This test case tries to create a cwe without a name
    # # Currently this is not handled in our code, hence we don't know what error it will throw
    # # To be replaced with the type of Error Thrown in future
    # # Defect "x" is raised for this
    # def test_cwe_compulsory_name_missing_field_check(self):
    #     with self.assertRaises(IntegrityError):
    #         CWE.objects.create(code=100)


class TestEditCWE(TestCase):

    def setUp(self):
        self._construct_test_database()

    def tearDown(self):
        self._destruct_test_database()

    def _construct_test_database(self):
        cwe101 = CWE(code=101, name="CWE #101")
        cwe101.save()
        cwe102 = CWE(code=102, name="CWE #102")
        cwe102.save()

    def _destruct_test_database(self):
        cwe101 = CWE.objects.get(code=101)
        cwe101.delete()
        cwe102 = CWE.objects.get(code=102)
        cwe102.delete()

    def test_positive_edit_name(self):
        # Retrieve the CWE object and change the name.
        cwe = CWE.objects.get(code=101)
        cwe.name = "CWE #101-changed"
        cwe.save()

        # Verify that the changed name has been written to database
        cwe = CWE.objects.get(code=101)
        self.assertEqual(cwe.name, "CWE #101-changed")

    def test_negative_edit_code_duplicated(self):
        cwe = CWE.objects.get(code=101)
        cwe.code = 102  # But 102 already exists
        with transaction.atomic():
            self.assertRaises(IntegrityError, cwe.save)


class KeywordMethodTests(TestCase):

    def setUp(self):
        Keyword.objects.create(name="Authentication")
        Keyword.objects.create(name="Injection")

    # This is a positive test case which checks if the various category got created or not
    def test_keyword_name_got_created(self):
        # validate it with what we created in the setUp Method
        self.assertIsNotNone(Keyword.objects.get(name="authent"))
        self.assertIsNotNone(Keyword.objects.get(name="inject"))

    # This test case checks if only unique CWE Keywords are created
    # If we try to create the  category with the same name, it should throw an Integrity Error
    def test_keyword_name_created_validate(self):
        with self.assertRaises(IntegrityError):
            Keyword.objects.create(name="Authentication")

    # This test case checks if only unique CWE Keywords are created and case insensitive
    # If we try to create the  category with the same name, it should throw an Integrity Error
    def test_keyword_name_created_validate_case(self):
        with self.assertRaises(IntegrityError):
            Keyword.objects.create(name="AUTHENTICATION")

    # This test case checks if only unique CWE Keywords are created and stemmed
    # If we try to create the  category with the same name, it should throw an Integrity Error
    def test_keyword_name_created_validate_stemmed(self):
        with self.assertRaises(IntegrityError):
            Keyword.objects.create(name="authent")

    # This test case validates the method which will give the name of the keyword
    # It also validates if the return type is a String
    def test_keyword_creation_method(self):
        keyword = Keyword.objects.get(name="authent")
        self.assertEqual(isinstance(keyword.__unicode__(), basestring), True)

    # This test checks that integer names can be saved successfully
    def test_keyword_integer_name(self):
        Keyword(name=404).save()
        kw = Keyword.objects.get(name="404")
        self.assertEqual(kw.name, "404")



class CategoryMethodTests(TestCase):

    def setUp(self):
        Category.objects.create(name="category1")
        Category.objects.create(name="category2")
        Category.objects.create(name="category3")
        Category.objects.create(name="category4")

    # This is a positive test case which checks if the various category got created or not
    def test_category_name_got_created(self):
        # Retrieve the name of the category which is being created
        category1 = Category.objects.get(name="category1")
        category2 = Category.objects.get(name="category2")
        category3 = Category.objects.get(name="category3")
        category4 = Category.objects.get(name="category4")
        # validate it with what we created in the setUp Method
        self.assertEquals(category1.name, "category1")
        self.assertEquals(category2.name, "category2")
        self.assertEquals(category3.name, "category3")
        self.assertEquals(category4.name, "category4")

    # This test case checks if only unique CWE categories are created
    # If we try to create the  category with the same name, it should throw an Integrity Error
    def test_category_name_created_validate(self):
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="category1")

    # This test case checks if the category creation method returns the name
    # It also validates if the return type is a String
    def test_category_creation_method(self):
        category5 = Category.objects.create(name="Category5")
        self.assertEqual(category5.__unicode__(), category5.name)
        self.assertEqual(isinstance(category5.__unicode__(), basestring), True)
