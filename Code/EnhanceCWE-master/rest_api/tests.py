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
import json
import copy
from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.conf import settings
from allauth.account.models import EmailAddress
from rest_framework import status
from rest_framework.authtoken.models import Token
from cwe.models import CWE
from cwe.models import Keyword
from muo.models import MisuseCase
from muo.models import MUOContainer
from muo.models import UseCase
from rest_api.views import CWERelatedList
from rest_api.views import CWEAllList
from rest_api.views import CWESearchSingleString
from rest_api.views import MisuseCaseRelated
from rest_api.views import UseCaseRelated
from rest_api.views import SaveCustomMUO


class RestAPITestBase(TestCase):

    _cli = Client()     # The testing client

    AUTH_TOKEN_TYPE_ACTIVE_USER = 0
    AUTH_TOKEN_TYPE_INACTIVE_USER = 1
    AUTH_TOKEN_TYPE_NONE = 2

    VERY_LARGE_NUM = "999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999"

    def setUp(self):
        self.set_up_users_and_tokens()
        self.set_up_test_data()

    def tearDown(self):
        self.tear_down_test_data()
        self.tear_down_users_and_tokens()

    def set_up_users_and_tokens(self):
        self._user_1 = User(username='user_1', is_active=True)
        self._user_1.save()
        self._user_1_token = str(Token.objects.create(user=self._user_1))

        self._user_2 = User(username='user_2', is_active=True)
        self._user_2.save()
        self._user_2_token = str(Token.objects.create(user=self._user_2))

        self._user_3_inactive = User(username='user_3_inactive', is_active=False)
        self._user_3_inactive.save()
        self._user_3_inactive_id = self._user_3_inactive.id
        self._user_3_inactive_token = Token.objects.create(user=self._user_3_inactive)

    def set_up_test_data(self):
        # To be overridden by the subclass.
        pass

    def tear_down_users_and_tokens(self):
        Token.objects.all().delete()
        User.objects.all().delete()

    def tear_down_test_data(self):
        # To be overridden by the subclass.
        pass

    def http_get(self, url, params, auth_token_type=AUTH_TOKEN_TYPE_ACTIVE_USER):
        auth_token = self._user_1_token
        if auth_token_type == RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER:
            auth_token = self._user_3_inactive_token
        elif auth_token_type == RestAPITestBase.AUTH_TOKEN_TYPE_NONE:
            auth_token = None
        return self._cli.get(url, data=params, HTTP_AUTHORIZATION='Token '+str(auth_token))

    def http_post(self, url, data, auth_token_type=AUTH_TOKEN_TYPE_ACTIVE_USER):
        auth_token = self._user_1_token
        if auth_token_type == RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER:
            auth_token = self._user_3_inactive_token
        elif auth_token_type == RestAPITestBase.AUTH_TOKEN_TYPE_NONE:
            auth_token = None
        return self._cli.post(url, data, HTTP_AUTHORIZATION='Token '+str(auth_token))


class TestCWETextRelated(RestAPITestBase):

    CWE_CODES = [101, 102, 103]     # The CWE codes used in the tests
    KEYWORD_NAMES = ["authent", "overflow", "bypass"]      # The names of keywords

    def set_up_test_data(self):
        # Create the keywords
        kw_auth = Keyword(name=self.KEYWORD_NAMES[0])
        kw_auth.save()
        kw_overflow = Keyword(name=self.KEYWORD_NAMES[1])
        kw_overflow.save()
        kw_bypass = Keyword(name=self.KEYWORD_NAMES[2])
        kw_bypass.save()

        # Create the CWEs
        cwe101 = CWE(code=self.CWE_CODES[0], name="CWE #"+str(self.CWE_CODES[0]))
        cwe101.save()
        cwe101.keywords.add(kw_auth)    # Only one keyword

        cwe102 = CWE(code=self.CWE_CODES[1], name="CWE #"+str(self.CWE_CODES[1]))
        cwe102.save()
        cwe102.keywords.add(kw_overflow, kw_bypass)    # Multiple keywords

        cwe103 = CWE(code=self.CWE_CODES[2], name="CWE #"+str(self.CWE_CODES[2]))
        cwe103.save()
        cwe103.keywords.add(kw_overflow, kw_bypass)    # Multiple keywords

    def tear_down_test_data(self):
        # Delete all CWEs.
        CWE.objects.all().delete()
        # Delete all keywords.
        Keyword.objects.all().delete()

    # Helper methods

    def _get_base_url(self):
        return reverse("restapi_CWETextRelated")

    def _form_url_params(self, text):
        return {CWERelatedList.PARAM_TEXT: text}

    def _cwe_info_found(self, content, code):
        cwe_repr = "{\"id\":" + str(code-100) + ",\"code\":" + str(code) + ",\"name\":\"CWE #" + str(code) + "\"}"
        return cwe_repr in content

    def _cwe_info_empty(self, content):
        return content == '[]'

    # Positive test cases

    def test_positive_search_text_1_keyword(self):
        text = "authentication fails because ..."
        response = self.http_get(self._get_base_url(), self._form_url_params(text))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)

    def test_positive_search_text_multiple_keywords(self):
        text = "the user can bypass the file access check due to a stack overflow caused by ..."
        response = self.http_get(self._get_base_url(), self._form_url_params(text))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_search_text_multiple_keywords_with_limit(self):
        max_return = CWERelatedList.CWE_MAX_RETURN
        CWERelatedList.CWE_MAX_RETURN = 1   # Only return one CWE.
        text = "the user can bypass the file access check due to a stack overflow caused by ..."
        response = self.http_get(self._get_base_url(), self._form_url_params(text))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)
        CWERelatedList.CWE_MAX_RETURN = max_return

    # Negative test cases

    def test_negative_search_text_no_match(self):
        text = "the password is leaked because the security level is incorrectly set..."
        response = self.http_get(self._get_base_url(), self._form_url_params(text))
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)

    def test_negative_no_authentication_token(self):
        text = "the password is leaked because the security level is incorrectly set..."
        response = self.http_get(self._get_base_url(), self._form_url_params(text),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        text = "the password is leaked because the security level is incorrectly set..."
        response = self.http_get(self._get_base_url(), self._form_url_params(text),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestCWEAllList(RestAPITestBase):

    CWE_CODES = [101, 102, 103]     # The CWE codes used in the tests

    def set_up_test_data(self):
        # Construct the test database
        for code in self.CWE_CODES:
            cwe = CWE(code=code, name="CWE #"+str(code))
            cwe.save()

    def tear_down_test_data(self):
        # Destruct the test database
        for code in self.CWE_CODES:
            cwe = CWE.objects.get(code=code)
            cwe.delete()

    # Helper methods

    def _get_base_url(self):
        return reverse("restapi_CWEAll")

    def _form_url_params(self, offset=None, limit=None, code=None, name_contains=None):
        params = dict()
        if offset is not None:
            params[CWEAllList.PARAM_OFFSET] = str(offset)
        if limit is not None:
            params[CWEAllList.PARAM_LIMIT] = str(limit)
        if code is not None:
            params[CWEAllList.PARAM_CODE] = str(code)
        if name_contains is not None:
            params[CWEAllList.PARAM_NAME_CONTAINS] = str(name_contains)
        return params

    def _cwe_total_count(self, content):
        result = json.loads(content)
        return result[CWEAllList.RESPONSE_KEY_TOTAL_COUNT]

    def _cwe_info_found(self, content, code):
        result = json.loads(content)
        found = False
        for cwe_object in result[CWEAllList.RESPONSE_KEY_CWE_OBJECTS]:
            if (cwe_object['id'] == code-100 and
                    cwe_object['code'] == code and
                    cwe_object['name'] == "CWE #"+str(code)):
                found = True
                break
        return found

    def _cwe_info_empty(self, content):
        result = json.loads(content)
        return len(result[CWEAllList.RESPONSE_KEY_CWE_OBJECTS]) == 0

    # Positive test cases

    def test_positive_get_default_default(self):
        original_max_return = CWEAllList.MAX_RETURN
        CWEAllList.DEFAULT_LIMIT = 2  # For test purpose we only return at most two CWEs.
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=None, limit=None))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        CWEAllList.MAX_RETURN = original_max_return

    def test_positive_get_2_default(self):
        CWEAllList.DEFAULT_LIMIT = 2  # For test purpose we only return at most two CWEs.
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=None))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_default_2(self):
        original_max_return = CWEAllList.MAX_RETURN
        CWEAllList.DEFAULT_OFFSET = 0  # For test purpose we only return at most two CWEs.
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=None, limit=2))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        CWEAllList.MAX_RETURN = original_max_return

    def test_positive_get_0_0(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=0))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_positive_get_0_1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=1))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)

    def test_positive_get_0_2(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=2))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)

    def test_positive_get_0_10(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=10))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_2_0(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=0))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_positive_get_2_1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=1))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_2_10(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=10))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_0_1_max_2(self):
        original_max_return = CWEAllList.MAX_RETURN
        CWEAllList.MAX_RETURN = 2
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        CWEAllList.MAX_RETURN = original_max_return

    def test_positive_get_0_10_max_2(self):
        original_max_return = CWEAllList.MAX_RETURN
        CWEAllList.MAX_RETURN = 2
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=10))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)
        CWEAllList.MAX_RETURN = original_max_return

    def test_positive_get_0_3_102_None(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=3, code=102))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 1)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)

    def test_positive_get_0_3_None_CWE(self):
        response = self.http_get(self._get_base_url(),
                                 self._form_url_params(offset=0, limit=3, name_contains="CWE"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), True)

    def test_positive_get_0_2_None_CWE(self):
        response = self.http_get(self._get_base_url(),
                                 self._form_url_params(offset=0, limit=2, name_contains="CWE"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)

    # Negative test cases

    def test_negative_get_3_default(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=3, limit=None))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_very_large_offset(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=self.VERY_LARGE_NUM, limit=None))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_3_0(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=3, limit=0))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_3_1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=3, limit=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_3_10(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=3, limit=10))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_0_very_large_limit(self):
        original_max_return = CWEAllList.MAX_RETURN
        CWEAllList.MAX_RETURN = 2
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=self.VERY_LARGE_NUM))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=101), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=102), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=103), False)
        CWEAllList.MAX_RETURN = original_max_return

    def test_negative_get_n1_1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=-1, limit=1))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_1_n1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=1, limit=-1))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_invalid_inputs(self):
        invalid_inputs = [
            ("0", "a"),     # 'limit' is not integer.
            ("0", "1a"),    # 'limit' is not integer.
            ("0", "a1"),    # 'limit' is not integer.
            ("a", "1"),     # 'offset' is not integer.
            ("1a", "1"),    # 'offset' is not integer.
            ("a1", "1"),    # 'offset' is not integer.
        ]
        for input_pair in invalid_inputs:
            response = self.http_get(self._get_base_url(), self._form_url_params(input_pair[0], input_pair[1]))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_no_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=1),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=1),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_get_0_2_None_name(self):
        response = self.http_get(self._get_base_url(),
                                 self._form_url_params(offset=0, limit=2, name_contains="name"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 0)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_0_3_code_name_contains_both_present(self):
        response = self.http_get(self._get_base_url(),
                                 self._form_url_params(offset=0, limit=3, code=102, name_contains="CWE"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_0_3_abc_None(self):
        invalid_codes = [
            "102a",
            "a102",
            "abc",
            "+-*/"
        ]
        for invalid_code in invalid_codes:
            response = self.http_get(self._get_base_url(),
                                     self._form_url_params(offset=0, limit=3, code=invalid_code))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestCWESearchSingleString(RestAPITestBase):

    CWE_CODES = [0, 1, 11]     # The CWE codes used in the tests
    CWE_ID_MAP = {0: 1, 1: 2, 11: 3}     # The CWE's IDs.

    def set_up_test_data(self):
        # Construct the test database
        for code in self.CWE_CODES:
            cwe = CWE(code=code, name="CWE #"+str(code))
            cwe.save()

    def tear_down_test_data(self):
        # Destruct the test database
        for code in self.CWE_CODES:
            cwe = CWE.objects.get(code=code)
            cwe.delete()

    # Helper methods

    def _get_base_url(self):
        return reverse("restapi_CWESearchSingleString")

    def _form_url_params(self, offset=None, limit=None, search_str=None):
        params = dict()
        if offset is not None:
            params[CWESearchSingleString.PARAM_OFFSET] = str(offset)
        if limit is not None:
            params[CWESearchSingleString.PARAM_LIMIT] = str(limit)
        if search_str is not None:
            params[CWESearchSingleString.PARAM_SEARCH_STR] = str(search_str)
        return params

    def _cwe_total_count(self, content):
        result = json.loads(content)
        return result[CWESearchSingleString.RESPONSE_KEY_TOTAL_COUNT]

    def _cwe_info_found(self, content, code):
        result = json.loads(content)
        found = False
        for cwe_object in result[CWESearchSingleString.RESPONSE_KEY_CWE_OBJECTS]:
            if (cwe_object['id'] == self.CWE_ID_MAP[code] and
                    cwe_object['code'] == code and
                    cwe_object['name'] == "CWE #"+str(code)):
                found = True
                break
        return found

    def _cwe_info_empty(self, content):
        result = json.loads(content)
        return len(result[CWESearchSingleString.RESPONSE_KEY_CWE_OBJECTS]) == 0

    # Positive test cases

    def test_positive_get_default_default(self):
        original_max_return = CWESearchSingleString.MAX_RETURN
        CWESearchSingleString.DEFAULT_LIMIT = 2  # For test purpose we only return at most two CWEs.
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=None, limit=None))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), True)
        CWESearchSingleString.MAX_RETURN = original_max_return

    def test_positive_get_2_default(self):
        original_max_return = CWESearchSingleString.MAX_RETURN
        CWESearchSingleString.MAX_RETURN = 2  # For test purpose we only return at most two CWEs.
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=None))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), True)
        CWESearchSingleString.MAX_RETURN = original_max_return

    def test_positive_get_default_2(self):
        original_max_return = CWESearchSingleString.MAX_RETURN
        CWESearchSingleString.DEFAULT_OFFSET = 0  # For test purpose we only return at most two CWEs.
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=None, limit=2))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), False)
        CWESearchSingleString.MAX_RETURN = original_max_return

    def test_positive_get_0_0(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=0))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_positive_get_0_1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=1))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), False)

    def test_positive_get_0_2(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=2))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), False)

    def test_positive_get_0_10(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=10))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), True)

    def test_positive_get_2_0(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=0))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_positive_get_2_1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=1))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), True)

    def test_positive_get_2_10(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=10))
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), True)

    def test_positive_get_0_1_max_2(self):
        original_max_return = CWESearchSingleString.MAX_RETURN
        CWESearchSingleString.MAX_RETURN = 2
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), False)
        CWESearchSingleString.MAX_RETURN = original_max_return

    def test_positive_get_0_10_max_2(self):
        original_max_return = CWESearchSingleString.MAX_RETURN
        CWESearchSingleString.MAX_RETURN = 2
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=10))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), False)
        CWESearchSingleString.MAX_RETURN = original_max_return

    def test_positive_get_0_3_1_None(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=3, search_str="1"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 2)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), False)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), True)

    def test_positive_get_0_3_None_CWE(self):
        response = self.http_get(self._get_base_url(),
                                 self._form_url_params(offset=0, limit=3, search_str="CWE"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), True)

    def test_positive_get_0_2_None_CWE(self):
        response = self.http_get(self._get_base_url(),
                                 self._form_url_params(offset=0, limit=2, search_str="CWE"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), False)

    def test_negative_get_0_3_abc_None(self):
        search_strings = [
            "102a",
            "a102",
            "abc",
            "+-*/"
        ]
        for search_string in search_strings:
            response = self.http_get(self._get_base_url(),
                                     self._form_url_params(offset=0, limit=3, search_str=search_string))
            self.assertEqual(self._cwe_total_count(content=response.content), 0)
            self.assertTrue(self._cwe_info_empty(content=response.content))

    # Negative test cases

    def test_negative_get_3_default(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=3, limit=None))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_very_large_offset(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=self.VERY_LARGE_NUM, limit=None))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_3_0(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=3, limit=0))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_3_1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=3, limit=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_3_10(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=3, limit=10))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertTrue(self._cwe_info_empty(content=response.content))

    def test_negative_get_0_very_large_limit(self):
        original_max_return = CWESearchSingleString.MAX_RETURN
        CWESearchSingleString.MAX_RETURN = 2
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=0, limit=self.VERY_LARGE_NUM))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 3)
        self.assertEqual(self._cwe_info_found(content=response.content, code=0), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=1), True)
        self.assertEqual(self._cwe_info_found(content=response.content, code=11), False)
        CWESearchSingleString.MAX_RETURN = original_max_return

    def test_negative_get_n1_1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=-1, limit=1))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_get_1_n1(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=1, limit=-1))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_invalid_inputs(self):
        invalid_inputs = [
            ("0", "a"),     # 'limit' is not integer.
            ("0", "1a"),    # 'limit' is not integer.
            ("0", "a1"),    # 'limit' is not integer.
            ("a", "1"),     # 'offset' is not integer.
            ("1a", "1"),    # 'offset' is not integer.
            ("a1", "1"),    # 'offset' is not integer.
        ]
        for input_pair in invalid_inputs:
            response = self.http_get(self._get_base_url(), self._form_url_params(input_pair[0], input_pair[1]))
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_no_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=1),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(offset=2, limit=1),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_get_0_2_None_name(self):
        response = self.http_get(self._get_base_url(),
                                 self._form_url_params(offset=0, limit=2, search_str="name"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self._cwe_total_count(content=response.content), 0)
        self.assertTrue(self._cwe_info_empty(content=response.content))


class TestMisuseCaseSuggestion(RestAPITestBase):

    CWE_CODES = [101, 102, 103]     # The CWE codes used in the tests

    def _create_muo_and_misuse_case(self, cwes, muc_desc, custom, approved, creator):
        # Create the MUO container
        cwe_code_list = [cwe.code for cwe in cwes]
        muc_dict = copy.deepcopy(SaveCustomMUO.TEMPLATE_MISUSE_CASE)
        muc_dict["misuse_case_description"] = muc_desc
        uc_dict = copy.deepcopy(SaveCustomMUO.TEMPLATE_USE_CASE)
        uc_dict["use_case_description"] = ""
        uc_dict["osr"] = ""
        MUOContainer.create_custom_muo(cwe_code_list,
                                       misusecase=muc_dict,
                                       usecase=uc_dict,    # Use Case is not important here.
                                       created_by=creator
                                       )
        # We can find this MUO container because only one misuse case is associated with it.
        muo = MUOContainer.objects.get(misuse_case__misuse_case_description=muc_desc)

        if not custom:
            # This is not a custom MUO. We need to change its is_custom field.
            muo.is_custom = False

        if approved:
            # By default, the newly created MUO container is in 'draft' state.
            # If it should be in 'approved' state, we need to submit and approve it.
            muo.action_submit()
            muo.action_approve()

    def set_up_test_data(self):
        # Create CWEs.
        cwe101 = CWE(code=self.CWE_CODES[0])
        cwe101.save()
        cwe102 = CWE(code=self.CWE_CODES[1])
        cwe102.save()
        cwe103 = CWE(code=self.CWE_CODES[2])
        cwe103.save()

        # Create the MUO containers and misuse cases.
        self._create_muo_and_misuse_case(cwes=[cwe101],
                                         muc_desc="Misuse Case 1",
                                         custom=False,
                                         approved=True,     # Approved, so it's generic.
                                         creator=self._user_1)
        self._create_muo_and_misuse_case(cwes=[cwe102],
                                         muc_desc="Misuse Case 2",
                                         custom=True,
                                         approved=True,     # Approved, so it's generic but also custom.
                                         creator=self._user_1)
        self._create_muo_and_misuse_case(cwes=[cwe102, cwe103],
                                         muc_desc="Misuse Case 3",
                                         custom=True,
                                         approved=False,    # Not approved, so it's custom.
                                         creator=self._user_1)
        self._create_muo_and_misuse_case(cwes=[cwe102],
                                         muc_desc="Misuse Case 4",
                                         custom=True,
                                         approved=False,    # Not approved, so it's custom.
                                         creator=self._user_1)
        self._create_muo_and_misuse_case(cwes=[cwe103],
                                         muc_desc="Misuse Case 5",
                                         custom=True,
                                         approved=False,    # Not approved, so it's custom.
                                         creator=self._user_2)  # By another user

    def tear_down_test_data(self):
        # Reject all the MUO containers before deleting them.
        for muo in MUOContainer.objects.all():
            if muo.status == 'approved':
                muo.action_reject(reject_reason="In order to delete the test data.")
        # Delete all the MUO containers.
        MUOContainer.objects.all().delete()
        # Delete all the misuse cases.
        MisuseCase.objects.all().delete()
        # Delete all the CWEs.
        CWE.objects.all().delete()

    # Helper methods

    def _get_base_url(self):
        return reverse("restapi_MisuseCase_CWERelated")

    def _form_url_params(self, cwe_code_list):
        cwes_str = "".join(str(code)+"," for code in cwe_code_list).rstrip(',')
        return {MisuseCaseRelated.PARAM_CWES: cwes_str}

    def _misuse_case_info_found(self, json_content, mu_index):
        mu_name = "MU-0000" + str(mu_index)
        mu_description = "Misuse Case " + str(mu_index)
        found = False
        for json_mu in json_content:
            if (json_mu['id'] == mu_index
                    and json_mu['name'] == mu_name
                    and json_mu['misuse_case_description'] == mu_description):
                found = True
                break
        return found

    # Positive test cases

    def test_positive_single_cwe(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([self.CWE_CODES[0]]))
        json_content = json.loads(response.content)
        # Make sure exactly one misuse case is returned.
        self.assertEqual(len(json_content), 1)
        # Make sure the first misuse case is returned.
        self.assertEqual(self._misuse_case_info_found(json_content, 1), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 2), False)
        self.assertEqual(self._misuse_case_info_found(json_content, 3), False)
        self.assertEqual(self._misuse_case_info_found(json_content, 4), False)
        self.assertEqual(self._misuse_case_info_found(json_content, 5), False)

    def test_positive_multiple_cwes(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([self.CWE_CODES[0], self.CWE_CODES[2]]))
        json_content = json.loads(response.content)
        # Make sure exactly two misuse cases are returned.
        self.assertEqual(len(json_content), 2)
        # Make sure the first, and third misuse cases are returned.
        self.assertEqual(self._misuse_case_info_found(json_content, 1), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 2), False)
        self.assertEqual(self._misuse_case_info_found(json_content, 3), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 4), False)
        self.assertEqual(self._misuse_case_info_found(json_content, 5), False)

    def test_positive_all_cwes(self):
        response = self.http_get(self._get_base_url(), self._form_url_params(self.CWE_CODES))
        json_content = json.loads(response.content)
        self.assertEqual(len(json_content), 4)
        self.assertEqual(self._misuse_case_info_found(json_content, 1), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 2), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 3), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 4), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 5), False)

    def test_positive_distinct_misuse_cases(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([self.CWE_CODES[1], self.CWE_CODES[2]]))
        json_content = json.loads(response.content)
        # Both keyword #102 and #103 are associated with both misuse case #3.
        # We want to make sure that the same misuse case is returned only once.
        self.assertEqual(len(json_content), 3)
        self.assertEqual(self._misuse_case_info_found(json_content, 1), False)
        self.assertEqual(self._misuse_case_info_found(json_content, 2), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 3), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 4), True)
        self.assertEqual(self._misuse_case_info_found(json_content, 5), False)

    # Negative test cases

    def test_negative_very_large_cwe_id(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([self.VERY_LARGE_NUM]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_malformed_cwes(self):
        cwes_str_list = [
            "",     # Empty code list
            "101,102,",     # Additional ',' at the end
            "101|102",  # Not using ',' as separator
            "101.1,102.2",  # Not using integers
            "10a",  # Not using numeric values
            "10a,20b"   # Not using numeric values
        ]
        for cwes_str in cwes_str_list:
            # Note we cannot use the _get_base_url() and _form_url_params() because these two methods
            # will construct a valid Http request, while here we want an invalid one.
            response = self.http_get(self._get_base_url()+'?'+MisuseCaseRelated.PARAM_CWES+'='+cwes_str, None)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            # Make sure the error message is generated using this method.
            self.assertEqual(response.content,
                             # Because response.content has been JSONized, we need to JSONize the
                             # error message in order to compare for equality.
                             str(json.dumps(MisuseCaseRelated()._form_err_msg_malformed_cwes(cwes_str)))
                             )

    def test_negative_not_found_cwes(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([101, 102, 103, 104, 105]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Make sure the error message is generated using this method.
        self.assertEqual(response.content,
                         # Because response.content has been JSONized, we need to JSONize the
                         # error message in order to compare for equality.
                         str(json.dumps(MisuseCaseRelated()._form_err_msg_cwes_not_found([104, 105])))
                         )

    def test_negative_no_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([self.CWE_CODES[0]]),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([self.CWE_CODES[0]]),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUseCaseSuggestion(RestAPITestBase):

    DESCRIPTION_BASE_MISUSE_CASE = "Misuse Case "     # Don't forget the trailing blank space.
    DESCRIPTION_BASE_USE_CASE = "Use Case "     # Don't forget the trailing blank space.
    DESCRIPTION_BASE_OSR = "Overlooked Security Requirement "   # Don't forget the trailing blank space.

    def _create_muo_and_misuse_case(self, cwes, muc_desc, custom, creator):
        # Create the misuse case and establish the relationship with the CWEs
        misuse_case = MisuseCase(misuse_case_description=muc_desc,
                                 created_by=creator
                                 )
        misuse_case.save()
        misuse_case.cwes.add(*cwes)  # Establish the relationship between the misuse case and CWEs

        # Create the MUO container for the misuse case and establish the relationship between the
        # MUO Container and CWEs
        muo_container = MUOContainer(is_custom=custom,
                                     status='draft',
                                     misuse_case=misuse_case,
                                     created_by=creator
                                     )
        muo_container.save()
        muo_container.cwes.add(*cwes)   # Establish the relationship between the muo container and cwes

        return misuse_case, muo_container

    def _create_use_case_and_link_muo(self, index, muc, muo, creator):
        uc = UseCase(use_case_description=self.DESCRIPTION_BASE_USE_CASE+str(index),
                     osr=self.DESCRIPTION_BASE_OSR+str(index),
                     created_by=creator
                     )
        uc.muo_container = muo
        uc.misuse_case = muc
        uc.save()

    def _approve_muo_container(self, muo_container):
        muo_container.action_submit()
        muo_container.action_approve()

    def set_up_test_data(self):
        # Create some CWEs.
        cwe101 = CWE(code=101)
        cwe101.save()
        cwe102 = CWE(code=102)
        cwe102.save()
        cwe103 = CWE(code=103)
        cwe103.save()

        # Create the MUO containers and misuse cases.
        muc1, muo1 = self._create_muo_and_misuse_case(
            cwes=[cwe101],
            muc_desc="Misuse Case 1",
            custom=False,
            creator=self._user_1
        )
        muc2, muo2 = self._create_muo_and_misuse_case(
            cwes=[cwe102],
            muc_desc="Misuse Case 2",
            custom=True,
            creator=self._user_1
        )
        muc3, muo3 = self._create_muo_and_misuse_case(
            cwes=[cwe102, cwe103],
            muc_desc="Misuse Case 3",
            custom=True,
            creator=self._user_1
        )
        muc4, muo4 = self._create_muo_and_misuse_case(
            cwes=[cwe102],
            muc_desc="Misuse Case 4",
            custom=True,
            creator=self._user_1
        )
        muc5, muo5 = self._create_muo_and_misuse_case(
            cwes=[cwe103],
            muc_desc="Misuse Case 5",
            custom=True,
            creator=self._user_2
        )  # By another user

        # Create some use cases(with OSRs)
        self._create_use_case_and_link_muo(1, muc1, muo1, self._user_1)
        self._create_use_case_and_link_muo(2, muc2, muo2, self._user_1)
        self._create_use_case_and_link_muo(3, muc2, muo2, self._user_1)
        self._create_use_case_and_link_muo(4, muc3, muo3, self._user_1)
        self._create_use_case_and_link_muo(5, muc4, muo4, self._user_1)
        self._create_use_case_and_link_muo(6, muc4, muo4, self._user_1)
        self._create_use_case_and_link_muo(7, muc5, muo5, self._user_2)

        # Approve some of the MUO containers.
        self._approve_muo_container(muo1)
        self._approve_muo_container(muo2)

    def tear_down_test_data(self):
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

    def _get_base_url(self):
        return reverse("restapi_UseCase_MisuseCaseRelated")

    def _form_url_params(self, misuse_case_id_list):
        misuse_cases_str = "".join(str(code)+"," for code in misuse_case_id_list).rstrip(',')
        return {UseCaseRelated.PARAM_MISUSE_CASES: misuse_cases_str}

    def _use_case_info_found(self, json_content, uc_index):
        uc_name = "UC-{0:05d}".format(uc_index)
        uc_description = self.DESCRIPTION_BASE_USE_CASE + str(uc_index)
        osr = self.DESCRIPTION_BASE_OSR + str(uc_index)
        found = False
        for json_uc in json_content:
            if (json_uc['id'] == uc_index
                    and json_uc['name'] == uc_name
                    and json_uc['use_case_description'] == uc_description
                    and json_uc['osr'] == osr):
                found = True
                break
        return found

    # Positive test cases

    def test_positive_single_misuse_case(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([1]))
        json_content = json.loads(response.content)
        # Make sure exactly one use case is returned.
        self.assertEqual(len(json_content), 1)
        # Make sure the first use case is returned.
        self.assertEqual(self._use_case_info_found(json_content, 1), True)
        self.assertEqual(self._use_case_info_found(json_content, 2), False)
        self.assertEqual(self._use_case_info_found(json_content, 3), False)
        self.assertEqual(self._use_case_info_found(json_content, 4), False)
        self.assertEqual(self._use_case_info_found(json_content, 5), False)
        self.assertEqual(self._use_case_info_found(json_content, 6), False)
        self.assertEqual(self._use_case_info_found(json_content, 7), False)

    def test_positive_multiple_misuse_cases(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([1, 2]))
        json_content = json.loads(response.content)
        # Make sure all the use cases are returned.
        self.assertEqual(len(json_content), 3)
        # Make sure all the use cases are returned.
        self.assertEqual(self._use_case_info_found(json_content, 1), True)
        self.assertEqual(self._use_case_info_found(json_content, 2), True)
        self.assertEqual(self._use_case_info_found(json_content, 3), True)
        self.assertEqual(self._use_case_info_found(json_content, 4), False)
        self.assertEqual(self._use_case_info_found(json_content, 5), False)
        self.assertEqual(self._use_case_info_found(json_content, 6), False)
        self.assertEqual(self._use_case_info_found(json_content, 7), False)

    def test_positive_all_misuse_cases(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([n for n in range(1, 8)]))
        json_content = json.loads(response.content)
        # Make sure all the use cases are returned.
        self.assertEqual(len(json_content), 6)
        # Make sure all the use cases are returned.
        self.assertEqual(self._use_case_info_found(json_content, 1), True)
        self.assertEqual(self._use_case_info_found(json_content, 2), True)
        self.assertEqual(self._use_case_info_found(json_content, 3), True)
        self.assertEqual(self._use_case_info_found(json_content, 4), True)
        self.assertEqual(self._use_case_info_found(json_content, 5), True)
        self.assertEqual(self._use_case_info_found(json_content, 6), True)
        self.assertEqual(self._use_case_info_found(json_content, 7), False)

    # Negative test cases

    def test_negative_very_large_misuse_case_id(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([self.VERY_LARGE_NUM]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_malformed_misuse_cases(self):
        misuse_cases_str_list = [
            "",     # Empty id list
            "1,2,",     # Additional ',' at the end
            "1|2",  # Not using ',' as separator
            "1.1,2.2",  # Not using integers
            "1a",  # Not using numeric values
            "1a,2b"   # Not using numeric values
        ]
        for misuse_cases_str in misuse_cases_str_list:
            # Note we cannot use the _get_base_url() and _form_url_params() because these two methods
            # will construct a valid Http request, while here we want an invalid one.
            response = self.http_get(self._get_base_url()+'?'+UseCaseRelated.PARAM_MISUSE_CASES+'='+misuse_cases_str,
                                     None)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            # Make sure the error message is generated using this method.
            self.assertEqual(response.content,
                             # Because response.content has been JSONized, we need to JSONize the
                             # error message in order to compare for equality.
                             str(json.dumps(UseCaseRelated()._form_err_msg_malformed_misuse_cases(misuse_cases_str)))
                             )

    def test_negative_no_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([1]),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_negative_inactive_authentication_token(self):
        response = self.http_get(self._get_base_url(), self._form_url_params([1]),
                                 auth_token_type=RestAPITestBase.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestSaveCustomMUO(RestAPITestBase):

    _cli = Client()

    CWE_CODES = [101, 102, 103]     # The CWE codes used in the tests
    CWE_IDS = []
    DESCRIPTION_MISUSE_CASE = "Sample Misuse Case Description"
    DESCRIPTION_USE_CASE = "Sample Use Case Description"
    DESCRIPTION_OSR = "Sample Overlooked Security Requirement Description"

    def set_up_test_data(self):
        # Clear the current CWE ID list.
        self.CWE_IDS = []

        # Create the CWEs
        cwe101 = CWE(code=self.CWE_CODES[0], name="CWE #"+str(self.CWE_CODES[0]))
        cwe101.save()
        self.CWE_IDS.append(cwe101.id)

        cwe102 = CWE(code=self.CWE_CODES[1], name="CWE #"+str(self.CWE_CODES[1]))
        cwe102.save()
        self.CWE_IDS.append(cwe102.id)

        cwe103 = CWE(code=self.CWE_CODES[2], name="CWE #"+str(self.CWE_CODES[2]))
        cwe103.save()
        self.CWE_IDS.append(cwe103.id)

    def tear_down_test_data(self):
        # Delete MUO containers.
        MUOContainer.objects.all().delete()
        # Delete misuse cases
        MisuseCase.objects.all().delete()
        # Delete use cases
        UseCase.objects.all().delete()

    def _form_base_url(self):
        return reverse("restapi_CustomMUO_Create")

    def _form_post_data(self, cwe_code_list, muc_desc, uc_desc, osr_desc):
        muc_dict = copy.deepcopy(SaveCustomMUO.TEMPLATE_MISUSE_CASE)
        muc_dict["misuse_case_description"] = muc_desc

        uc_dict = copy.deepcopy(SaveCustomMUO.TEMPLATE_USE_CASE)
        uc_dict["use_case_description"] = uc_desc
        uc_dict["osr"] = osr_desc

        return {SaveCustomMUO.PARAM_CWE_CODES: json.dumps(cwe_code_list),
                SaveCustomMUO.PARAM_MISUSE_CASE: json.dumps(muc_dict),
                SaveCustomMUO.PARAM_USE_CASE: json.dumps(uc_dict)
                }

    def test_positive_all_valid(self):
        base_url = self._form_base_url()
        data = self._form_post_data(cwe_code_list=[self.CWE_CODES[0]],      # One CWE code
                                    muc_desc="",     # Empty description
                                    uc_desc="",      # Empty description
                                    osr_desc=""      # Empty description
                                    )
        response = self.http_post(base_url, data)
        # The POST method returned OK.
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        # Verify the post-conditions.
        # One and only one MUO was created.
        self.assertEqual(MUOContainer.objects.count(), 1)
        # The CWEs are associated correctly.
        muo = MUOContainer.objects.all()[0]
        cwes = CWE.objects.filter(muo_container=muo)
        associated_cwe_ids = {int(cwe.id) for cwe in cwes}
        passed_in_cwe_ids = {self.CWE_IDS[0]}
        self.assertEqual(associated_cwe_ids, passed_in_cwe_ids)
        # The misuse case was created correctly.
        self.assertEqual(muo.misuse_case.misuse_case_description, "")
        # Verify use case & OSR.
        use_cases = UseCase.objects.filter(muo_container=muo)
        self.assertEqual(use_cases.count(), 1)
        uc = use_cases[0]
        self.assertEqual(uc.use_case_description, "")
        self.assertEqual(uc.osr, "")

    def test_positive_all_valid_2(self):
        base_url = self._form_base_url()
        data = self._form_post_data(cwe_code_list=self.CWE_CODES,      # Multiple CWE codes
                                    muc_desc=self.DESCRIPTION_MISUSE_CASE,   # Non-empty description
                                    uc_desc=self.DESCRIPTION_USE_CASE,       # Non-empty description
                                    osr_desc=self.DESCRIPTION_OSR        # Non-empty description
                                    )
        response = self.http_post(base_url, data)
        # The POST method returned OK.
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        # Verify the post-conditions.
        # One and only one MUO was created.
        self.assertEqual(MUOContainer.objects.count(), 1)
        # The CWEs are associated correctly.
        muo = MUOContainer.objects.all()[0]
        cwes = CWE.objects.filter(muo_container=muo)
        associated_cwe_ids = {int(cwe.id) for cwe in cwes}
        passed_in_cwe_ids = set(self.CWE_IDS)
        self.assertEqual(associated_cwe_ids, passed_in_cwe_ids)
        # The misuse case was created correctly.
        self.assertEqual(muo.misuse_case.misuse_case_description, self.DESCRIPTION_MISUSE_CASE)
        # Verify use case & OSR.
        use_cases = UseCase.objects.filter(muo_container=muo)
        self.assertEqual(use_cases.count(), 1)
        uc = use_cases[0]
        self.assertEqual(uc.use_case_description, self.DESCRIPTION_USE_CASE)
        self.assertEqual(uc.osr, self.DESCRIPTION_OSR)

    def test_negative_invalid_cwe_ids(self):
        invalid_cwes_str_list = [
            "",     # Empty code list
            "101,102,",     # Additional ',' at the end
            "101|102",  # Not using ',' as separator
            "101.1,102.2",  # Not using integers
            "10a",  # Not using numeric values
            "10a,20b"   # Not using numeric values
        ]
        base_url = self._form_base_url()
        for invalid_cwes_str in invalid_cwes_str_list:
            data = {SaveCustomMUO.PARAM_CWE_CODES: invalid_cwes_str,
                    SaveCustomMUO.PARAM_MISUSE_CASE: self.DESCRIPTION_MISUSE_CASE,
                    SaveCustomMUO.PARAM_USE_CASE: self.DESCRIPTION_USE_CASE,
                    }
            response = self.http_post(base_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(MUOContainer.objects.count(), 0)   # No MUO was created.
            self.assertEqual(MisuseCase.objects.count(), 0)     # No misuse cases was created.
            self.assertEqual(UseCase.objects.count(), 0)     # No use cases was created.

    def test_negative_inactive_user(self):
        base_url = self._form_base_url()
        data = self._form_post_data(cwe_code_list=self.CWE_CODES,      # Valid CWE codes
                                    muc_desc=self.DESCRIPTION_MISUSE_CASE,   # Non-empty description
                                    uc_desc=self.DESCRIPTION_USE_CASE,       # Non-empty description
                                    osr_desc=self.DESCRIPTION_OSR        # Non-empty description
                                    )
        response = self.http_post(base_url, data, auth_token_type=self.AUTH_TOKEN_TYPE_INACTIVE_USER)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(MUOContainer.objects.count(), 0)   # No MUO was created.
        self.assertEqual(MisuseCase.objects.count(), 0)     # No misuse cases was created.
        self.assertEqual(UseCase.objects.count(), 0)     # No use cases was created.

    def test_negative_no_auth(self):
        base_url = self._form_base_url()
        data = self._form_post_data(cwe_code_list=self.CWE_CODES,      # Valid CWE codes
                                    muc_desc=self.DESCRIPTION_MISUSE_CASE,   # Non-empty description
                                    uc_desc=self.DESCRIPTION_USE_CASE,       # Non-empty description
                                    osr_desc=self.DESCRIPTION_OSR        # Non-empty description
                                    )
        response = self.http_post(base_url, data, auth_token_type=self.AUTH_TOKEN_TYPE_NONE)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(MUOContainer.objects.count(), 0)   # No MUO was created.
        self.assertEqual(MisuseCase.objects.count(), 0)     # No misuse cases was created.
        self.assertEqual(UseCase.objects.count(), 0)     # No use cases was created.

    def test_negative_wrong_method(self):
        base_url = self._form_base_url()
        data = self._form_post_data(cwe_code_list=self.CWE_IDS,      # Multiple CWE ID
                                    muc_desc=self.DESCRIPTION_MISUSE_CASE,   # Non-empty description
                                    uc_desc=self.DESCRIPTION_USE_CASE,       # Non-empty description
                                    osr_desc=self.DESCRIPTION_OSR        # Non-empty description
                                    )
        response = self.http_get(base_url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # Make sure we return an error message that tells what should be done.
        self.assertEqual(response.content,
                         str(json.dumps(SaveCustomMUO._form_err_msg_method_not_allowed())))

    def test_negative_data_in_wrong_format(self):
        wrong_format_cases = [
            None,   # Wrong format: No parameters
            {10: 10},    # Wrong format: No parameters
            {"": ""},    # Wrong format: No parameters
            SaveCustomMUO.TEMPLATE_MISUSE_CASE,  # Wrong format: No parameters
            {
                SaveCustomMUO.PARAM_CWE_CODES: [101, 102, 103],     # Wrong format: Not a JSON string
                SaveCustomMUO.PARAM_MISUSE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_MISUSE_CASE),
                SaveCustomMUO.PARAM_USE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_USE_CASE)
            },
            {
                SaveCustomMUO.PARAM_CWE_CODES: "101,102,103",     # Wrong format: Not a JSON string
                SaveCustomMUO.PARAM_MISUSE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_MISUSE_CASE),
                SaveCustomMUO.PARAM_USE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_USE_CASE)
            },
            {
                SaveCustomMUO.PARAM_CWE_CODES: "{101,102,103}",     # Wrong format: A JSON string but not a list
                SaveCustomMUO.PARAM_MISUSE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_MISUSE_CASE),
                SaveCustomMUO.PARAM_USE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_USE_CASE)
            },
            {
                # Wrong format: A JSON string but not a list
                SaveCustomMUO.PARAM_CWE_CODES: "{101:101,102:102,103:103}",
                SaveCustomMUO.PARAM_MISUSE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_MISUSE_CASE),
                SaveCustomMUO.PARAM_USE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_USE_CASE)
            },
            {
                SaveCustomMUO.PARAM_CWE_CODES: json.dumps([101, 102, 103]),
                SaveCustomMUO.PARAM_MISUSE_CASE: SaveCustomMUO.TEMPLATE_MISUSE_CASE,  # Wrong format: Not a JSON string
                SaveCustomMUO.PARAM_USE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_USE_CASE)
            },
            {
                SaveCustomMUO.PARAM_CWE_CODES: json.dumps([101, 102, 103]),
                # A JSON string but not a dictionary
                SaveCustomMUO.PARAM_MISUSE_CASE: "[101, 102, 103]",
                SaveCustomMUO.PARAM_USE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_USE_CASE)
            },
            {
                SaveCustomMUO.PARAM_CWE_CODES: json.dumps([101, 102, 103]),
                # A JSON dictionary but missing a field.
                SaveCustomMUO.PARAM_MISUSE_CASE: json.dumps({"misuse_case_descripition": ""}),
                SaveCustomMUO.PARAM_USE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_USE_CASE)
            },
            {
                SaveCustomMUO.PARAM_CWE_CODES: json.dumps([101, 102, 103]),
                SaveCustomMUO.PARAM_MISUSE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_MISUSE_CASE),
                SaveCustomMUO.PARAM_USE_CASE: SaveCustomMUO.TEMPLATE_USE_CASE  # Wrong format: Not a JSON string
            },
            {
                SaveCustomMUO.PARAM_CWE_CODES: json.dumps([101, 102, 103]),
                SaveCustomMUO.PARAM_MISUSE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_MISUSE_CASE),
                SaveCustomMUO.PARAM_USE_CASE: "[101, 102, 103]"  # Not a JSON dictionary
            },
            {
                SaveCustomMUO.PARAM_CWE_CODES: json.dumps([101, 102, 103]),
                SaveCustomMUO.PARAM_MISUSE_CASE: json.dumps(SaveCustomMUO.TEMPLATE_MISUSE_CASE),
                SaveCustomMUO.PARAM_USE_CASE: json.dumps({"use_case_descripition": ""}),
            },
        ]
        base_url = self._form_base_url()
        for data in wrong_format_cases:
            response = self.http_post(base_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(MUOContainer.objects.count(), 0)   # No MUO was created.
            self.assertEqual(MisuseCase.objects.count(), 0)     # No misuse cases was created.
            self.assertEqual(UseCase.objects.count(), 0)     # No use cases was created.


class TokenCreationDeletion(TestCase):
    """
    Tests if the token is created for clients only.
    """

    ROLE_CLIENT = "client"
    ROLE_CONTRIBUTOR = "contributor"

    USER_NAME = "user"
    USER_EMAIL = "user@example.com"

    def tearDown(self):
        Token.objects.all().delete()
        EmailAddress.objects.all().delete()
        get_user_model().objects.all().delete()

    def _create_user(self, role):
        user = get_user_model().objects.create(username=role,
                                               email=role+"@example.com",
                                               is_staff=True,
                                               is_active=True
                                               )
        user.set_password("user_password")
        user.save()

        # Verify and approve the email
        email_obj = EmailAddress.objects.create(user=user,
                                                email=role+"@example.com",
                                                primary=True,
                                                verified=True,
                                                requested_role=role
                                                )
        email_obj.action_approve()
        email_obj.save()

        return user, email_obj

    def test_token_creation_for_contributor(self):
        """
        Test Point: If the user is registered as a contributor, there should be no token created for him/her.
        """

        # Create a user of role "contributor" and approve the email.
        contributor_user, contributor_email = self._create_user(TokenCreationDeletion.ROLE_CONTRIBUTOR)

        # Verify: Nothing happens to the token table.
        tokens = Token.objects.filter(user=contributor_user)
        self.assertEqual(tokens.count(), 0)

        # Reject the email.
        contributor_email.action_reject(reject_reason="For test purpose.")

        # Verify: Nothing happens to the token table.
        tokens = Token.objects.filter(user=contributor_user)
        self.assertEqual(tokens.count(), 0)

    def test_token_creation_rejection_for_client(self):
        """
        Test Point:
            1). If the user is registered as a client, there should be a token created for him/her.
            2). If the user of role "client" is rejected, the created token will be deleted.
        """

        # Create a user of role "client" and approve the email.
        client_user, client_email = self._create_user(TokenCreationDeletion.ROLE_CLIENT)

        # Verify: A token has been created for this user.
        tokens = Token.objects.filter(user=client_user)
        self.assertEqual(tokens.count(), 1)

        # Reject the email.
        client_email.action_reject(reject_reason="For test purpose.")

        # Verify: The created token has been deleted.
        tokens = Token.objects.filter(user=client_user)
        self.assertEqual(tokens.count(), 0)
