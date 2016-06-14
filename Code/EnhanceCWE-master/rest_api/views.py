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
import re
import json
from django.contrib.auth.models import User
from django.db.models import Q
from cwe.models import CWE
from cwe.cwe_search import CWESearchLocator
from muo.models import MUOContainer
from muo.models import UseCase
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_api.serializers import CWESerializer
from rest_api.serializers import MisuseCaseSerializer
from rest_api.serializers import UseCaseSerializer
from .settings import SUGGESTED_CWE_MAX_RETURN


# Constants
FIELD_LENGTH_CWE_NAME = 128
DJANGO_DB_INTEGER_FIELD_SAFE_UPPER_LIMIT = 2147483647


class CWEAllList(APIView):
    """
    List all the CWEs that are available in the database.
    """
    queryset = CWE.objects.all()
    serializer_class = CWESerializer

    PARAM_OFFSET = "offset"
    PARAM_LIMIT = "limit"
    PARAM_CODE = "code"
    PARAM_NAME_CONTAINS = "name_contains"

    DEFAULT_OFFSET = "0"  # The default value of offset in GET method
    DEFAULT_LIMIT = "10"   # The default value of limit in GET method
    MAX_RETURN = "20"  # 20 CWEs will be returned at most, regardless many is specified in "limit".

    RESPONSE_KEY_CWE_OBJECTS = "cwe_objects"
    RESPONSE_KEY_TOTAL_COUNT = "total_count"

    @staticmethod
    def _validate_parameter(value):
        # This regular expression matches integers like "1", "101", but not "+1", "-1", "1.2", "1.a", etc.
        # See [here](http://regexr.com/) for test.
        param_pattern_regex = r"^[0-9]+$"
        return re.match(param_pattern_regex, value) is not None

    @staticmethod
    def _validate_title_contains(title_contains):
        return len(title_contains) <= FIELD_LENGTH_CWE_NAME
    
    @staticmethod
    def _form_err_msg_not_positive_integer(param_name, param_value):
        return ("Invalid arguments: '" + param_name +
                "' should be a positive integer like '101', but now '" + param_name +
                "' = '" + param_value + "'")
    
    @staticmethod
    def _form_err_msg_both_present(param_name1, param_name2):
        return ("Invalid arguments: '" + param_name1 +
                "' and '" + param_name2 + "' should not be present at the same time."
                )
    
    @staticmethod
    def _form_err_msg_too_long(param_name, param_value):
        return ("Invalid argument: '" + param_name + "' should not be longer than " +
                str(FIELD_LENGTH_CWE_NAME) + " characters, but now '" +
                param_name + "' has " + str(len(param_value)) + " characters.")

    def get(self, request):
        """
        @brief: Return the CWE objects in the database.
        @param: [in] request: The HTTP request.
        @return: rest_framework.response.Response
        """

        # Get the value of 'offset' and validate it.
        offset_str = request.GET.get(self.PARAM_OFFSET)
        if offset_str is None:
            # No 'offset' is passed in.
            offset_str = self.DEFAULT_OFFSET
        else:
            # 'offset' is provided. Check if it is in the correct format.
            if self._validate_parameter(offset_str) is False:
                err_msg = self._form_err_msg_not_positive_integer(self.PARAM_OFFSET, offset_str)
                return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Get the value of 'limit' and validate it.
        limit_str = request.GET.get(self.PARAM_LIMIT)
        if limit_str is None:
            # No 'limit' is passed in.
            limit_str = self.DEFAULT_LIMIT
        else:
            # 'limit' is provided. Check if it is in the correct format.
            if self._validate_parameter(limit_str) is False:
                err_msg = self._form_err_msg_not_positive_integer(self.PARAM_LIMIT, limit_str)
                return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Get the values of 'code' and 'name_contains'.
        # When neither of them appears, that means no restriction will be applied to the search.
        # When either of them appears, that means one parameter will be applied to the search.
        # However, they should never appear at the same time, because we are implementing an
        # 'exclusive OR' operation.
        code_str = request.GET.get(self.PARAM_CODE)
        name_contains_str = request.GET.get(self.PARAM_NAME_CONTAINS)

        if (code_str is not None) and (name_contains_str is not None):
            # Make sure they never appear at the same time.
            err_msg = self._form_err_msg_both_present(self.PARAM_CODE, self.PARAM_NAME_CONTAINS)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)
        elif code_str is not None:
            # If only 'code' is present.
            if self._validate_parameter(code_str) is False:
                err_msg = self._form_err_msg_not_positive_integer(self.PARAM_CODE, code_str)
                return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)
        elif name_contains_str is not None:
            # If only 'name_contains' is present.
            if self._validate_title_contains(name_contains_str) is False:
                err_msg = self._form_err_msg_too_long(self.PARAM_NAME_CONTAINS, name_contains_str)
                return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Neither of them appears. Then we have nothing to validate.
            pass

        # 'offset' and 'limit' should be integers so we convert the offset_str and limit_str.
        offset = int(offset_str)
        limit = int(limit_str)
        limit = (limit if limit < self.MAX_RETURN else self.MAX_RETURN)
        # 'code' should be an integer, too.
        cwe_code = (int(code_str) if code_str is not None else None)
        # 'name_contains' should be a string, so we can directly use 'name_contains_str' and
        # don't need any conversion for it.

        # Now the arguments should be valid.
        cwe_objects = CWE.objects.all()
        # Filter the CWE objects according to CWE code OR name.
        if cwe_code is not None:
            cwe_objects = cwe_objects.filter(code=cwe_code)
        elif name_contains_str is not None:
            cwe_objects = cwe_objects.filter(name__icontains=name_contains_str)

        # Now we have all the CWE objects that meet the search criteria.
        # Count how many CWE objects there are totally before applying the offset and limit.
        # This total count is helpful for pagination.
        cwe_objects_total_count = cwe_objects.count()

        if offset < cwe_objects.count():
            cwe_returned = cwe_objects[offset:offset+limit]
        else:
            # If offset is too large and exceeds the size of CWE objects, we return an empty list.
            cwe_returned = list()
        
        serializer = CWESerializer(cwe_returned, many=True)
        
        # Return both the CWE objects and the total count.
        returned_data = {
            self.RESPONSE_KEY_CWE_OBJECTS: serializer.data,
            self.RESPONSE_KEY_TOTAL_COUNT: cwe_objects_total_count
        }

        return Response(data=returned_data)


class CWESearchSingleString(APIView):
    """
    @brief: Search the CWE with three parameters: offset, limit, and a single search string.
    """

    PARAM_OFFSET = "offset"
    PARAM_LIMIT = "limit"
    PARAM_SEARCH_STR = "search_str"

    DEFAULT_OFFSET = "0"  # The default value of offset in GET method
    DEFAULT_LIMIT = "10"   # The default value of limit in GET method
    MAX_RETURN = "20"  # 20 CWEs will be returned at most, regardless many is specified in "limit".

    RESPONSE_KEY_CWE_OBJECTS = "cwe_objects"
    RESPONSE_KEY_TOTAL_COUNT = "total_count"

    @staticmethod
    def _form_err_msg_not_positive_integer(param_name, param_value):
        return ("Invalid arguments: '" + param_name +
                "' should be a positive integer like '101', but now '" + param_name +
                "' = '" + param_value + "'")

    def get(self, request):
        """
        @brief: Return the CWE objects in the database.
        @param: [in] request: The HTTP request.
        @return: rest_framework.response.Response
        """

        # Get the value of 'offset' and validate it.
        offset_str = request.GET.get(self.PARAM_OFFSET)
        if offset_str is None:
            # No 'offset' is passed in.
            offset_str = self.DEFAULT_OFFSET
        else:
            # 'offset' is provided. Check if it is in the correct format.
            if not offset_str.isdigit():
                err_msg = self._form_err_msg_not_positive_integer(self.PARAM_OFFSET, offset_str)
                return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Get the value of 'limit' and validate it.
        limit_str = request.GET.get(self.PARAM_LIMIT)
        if limit_str is None:
            # No 'limit' is passed in.
            limit_str = self.DEFAULT_LIMIT
        else:
            # 'limit' is provided. Check if it is in the correct format.
            if not limit_str.isdigit():
                err_msg = self._form_err_msg_not_positive_integer(self.PARAM_LIMIT, limit_str)
                return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # 'offset' and 'limit' should be integers so we convert the offset_str and limit_str.
        offset = int(offset_str)
        limit = int(limit_str)
        limit = (limit if limit < self.MAX_RETURN else self.MAX_RETURN)

        # Get the value of 'search_str'.
        # Because the search_str could be either the CWE code OR part of the CWE title,
        # we can only treat it as an arbitrary string.
        search_str = request.GET.get(self.PARAM_SEARCH_STR)

        # Now the arguments should be valid.
        cwe_objects = CWE.objects.all()
        # Filter the CWE objects according to search_str. We search this string in code and name.
        if search_str is not None:
            if search_str.isdigit():
                # If search_str is in the form of an integer, then we search in 'code' or 'name'.
                cwe_objects = cwe_objects.filter(Q(code=search_str) | Q(name__icontains=search_str))
            else:
                # Otherwise, we only search in 'name'.
                cwe_objects = cwe_objects.filter(name__icontains=search_str)

        # Now we have all the CWE objects that meet the search criteria.
        # Count how many CWE objects there are totally before applying the offset and limit.
        # This total count is helpful for pagination.
        cwe_objects_total_count = cwe_objects.count()

        if offset < cwe_objects.count():
            cwe_returned = cwe_objects[offset:offset+limit]
        else:
            # If offset is too large and exceeds the size of CWE objects, we return an empty list.
            cwe_returned = list()

        serializer = CWESerializer(cwe_returned, many=True)

        # Return both the CWE objects and the total count.
        returned_data = {
            self.RESPONSE_KEY_CWE_OBJECTS: serializer.data,
            self.RESPONSE_KEY_TOTAL_COUNT: cwe_objects_total_count
        }

        return Response(data=returned_data)


class CWERelatedList(APIView):
    """
    @brief: List the CWEs that are related to the given text.
    """

    PARAM_TEXT = "text"

    # This allows the unit test to modify the max return dynamically
    # without having to modify the settings.py manually.
    CWE_MAX_RETURN = SUGGESTED_CWE_MAX_RETURN

    def get(self, request):
        """
        @brief: Return the CWE objects that are suggested given the text.
        @param: [in] request: The HTTP request.
        @return: rest_framework.response.Response
        """

        text = request.GET.get(self.PARAM_TEXT)

        # Get the suggested CWEs.
        cwe_count_tuples = CWESearchLocator.get_instance().search_cwes(text)
        cwe_list = [cwe_count_tuple[0] for cwe_count_tuple in cwe_count_tuples][0:self.CWE_MAX_RETURN]

        serializer = CWESerializer(cwe_list, many=True)

        return Response(data=serializer.data)


class MisuseCaseRelated(APIView):
    """
    @brief: List the misuse cases that are related to the specified CWEs.
    """

    PARAM_CWES = "cwes"

    @staticmethod
    def _validate_parameter(cwes_str):
        # This regular expression matches strings like "101" or "101,102,103".
        # See [here](http://regexr.com/) for test.
        param_pattern_regex = r"^([0-9]+,)*([0-9]+)$"
        return re.match(param_pattern_regex, cwes_str) is not None

    @staticmethod
    def _validate_cwe_code_range(cwe_id_set):
        # Values from -2147483648 to 2147483647 are safe in all databases supported by Django.
        # https://docs.djangoproject.com/en/1.8/ref/models/fields/#integerfield
        # We need to verify if the CWE code is too large to be converted to a database integer field.
        too_large_cwe_code_set = set()
        for cwe_code in cwe_id_set:
            if long(cwe_code) > DJANGO_DB_INTEGER_FIELD_SAFE_UPPER_LIMIT:
                too_large_cwe_code_set.add(cwe_code)
        return too_large_cwe_code_set

    @staticmethod
    def _get_distinct_cwe_codes(cwes_str):
        return set(cwes_str.split(','))

    @staticmethod
    def _form_err_msg_malformed_cwes(cwes_str):
        return ("CWE code list is malformed: '" + cwes_str + "'. " +
                "It should be one or more positive integers separated by comma."
                )

    @staticmethod
    def _form_err_msg_too_large_cwe_code(too_large_cwe_codes):
        return ("The following CWE codes are too large(acceptable range is from 0 to 2147483647): " +
                ("".join(str(cwe_code)+',' for cwe_code in too_large_cwe_codes)).rstrip(',')
                )

    @staticmethod
    def _form_err_msg_cwes_not_found(cwe_codes_not_found):
        err_msg = ("The CWE of the following codes are not found: " +
                   ''.join(str(code)+"," for code in cwe_codes_not_found)
                   )
        return err_msg

    def get(self, request):
        """
        :param request: The HTTP request.
        :return: rest_framework.response.Response
        """

        # Get the "cwes" parameter value.
        cwes_str = request.GET.get(self.PARAM_CWES)

        # Validate the parameter or throw exception.
        if self._validate_parameter(cwes_str=cwes_str) is False:
            err_msg = self._form_err_msg_malformed_cwes(cwes_str)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Get the CWE codes from the parameter string.
        cwe_code_set = self._get_distinct_cwe_codes(cwes_str=cwes_str)

        # Check if any CWE code is too large.
        too_large_cwe_codes = self._validate_cwe_code_range(cwe_code_set)
        if len(too_large_cwe_codes) > 0:
            err_msg = self._form_err_msg_too_large_cwe_code(too_large_cwe_codes)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Get the current user.
        curr_user = request.user

        # Create the set of returned unique misuse case.
        misuse_case_set = set()

        # Try to get all the CWE objects.
        cwes = CWE.objects.filter(code__in=cwe_code_set)

        # If there is any CWE not found, then we return an error.
        cwe_codes_fetched = set([str(cwe.code) for cwe in cwes])
        cwe_codes_not_found = cwe_code_set - cwe_codes_fetched

        if len(cwe_codes_not_found) > 0:
            err_msg = self._form_err_msg_cwes_not_found(cwe_codes_not_found)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Find the misuse cases that are related to the CWEs.
        for cwe in cwes:
            # First, find all the MUO containers associated with the CWEs.
            cwe_misuse_cases_generic = cwe.misuse_cases.approved()
            cwe_misuse_cases_custom = cwe.misuse_cases.filter(created_by=curr_user).custom().draft()
            # Join the two sets
            misuse_case_set |= set(cwe_misuse_cases_generic | cwe_misuse_cases_custom)

        serializer = MisuseCaseSerializer(misuse_case_set, many=True)

        return Response(data=serializer.data, exception=Exception())


class UseCaseRelated(APIView):
    """
    @brief: List the misuse cases that are related to the specified CWEs.
    """

    PARAM_MISUSE_CASES = "misuse_cases"

    @staticmethod
    def _validate_parameter(misuse_cases_str):
        # This regular expression matches strings like "1" or "1,2,3".
        # See [here](http://regexr.com/) for test.
        param_pattern_regex = r"^([0-9]+,)*([0-9]+)$"
        return re.match(param_pattern_regex, misuse_cases_str) is not None

    @staticmethod
    def _validate_misuse_case_id_range(misuse_case_id_set):
        # Values from -2147483648 to 2147483647 are safe in all databases supported by Django.
        # https://docs.djangoproject.com/en/1.8/ref/models/fields/#integerfield
        # We need to verify if the misuse case ID is too large to be converted to a database integer field.
        too_large_muc_id_set = set()
        for muc_id in misuse_case_id_set:
            if long(muc_id) > DJANGO_DB_INTEGER_FIELD_SAFE_UPPER_LIMIT:
                too_large_muc_id_set.add(muc_id)
        return too_large_muc_id_set

    @staticmethod
    def _get_distinct_misuse_case_ids(misuse_cases_str):
        return set(misuse_cases_str.split(','))

    @staticmethod
    def _form_err_msg_malformed_misuse_cases(misuse_cases_str):
        return ("Misuse case ID list is malformed: '" + misuse_cases_str + "'. " +
                "It should be one or more positive integers separated by comma."
                )

    @staticmethod
    def _form_err_msg_too_large_misuse_case_ids(too_large_misuse_case_ids):
        return ("The following misuse case IDs are too large(acceptable range is from 0 to 2147483647): " +
                ("".join(str(muc_id)+',' for muc_id in too_large_misuse_case_ids)).rstrip(',')
                )

    def get(self, request):
        """
        :param request: The HTTP request.
        :return: rest_framework.response.Response
        """

        # Get the "misuse_cases" parameter value.
        misuse_cases_str = request.GET.get(self.PARAM_MISUSE_CASES)

        # Validate the parameter or throw exception.
        if self._validate_parameter(misuse_cases_str=misuse_cases_str) is False:
            err_msg = self._form_err_msg_malformed_misuse_cases(misuse_cases_str)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Get the current user.
        curr_user = request.user

        # Get the misuse case IDs from the parameter string.
        misuse_case_id_set = self._get_distinct_misuse_case_ids(misuse_cases_str=misuse_cases_str)

        # Check if any misuse case ID is too large.
        too_large_muc_ids = self._validate_misuse_case_id_range(misuse_case_id_set)
        if len(too_large_muc_ids) > 0:
            err_msg = self._form_err_msg_too_large_misuse_case_ids(too_large_muc_ids)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Get all the use cases that refer to these misuse cases.
        use_cases_related = UseCase.objects.filter(misuse_case_id__in=misuse_case_id_set)
        use_cases_generic = use_cases_related.approved()
        use_cases_custom = use_cases_related.filter(created_by=curr_user).custom().draft()

        # Get all the use cases to be returned.
        use_cases = use_cases_generic | use_cases_custom

        # Remove the duplicated use cases, if there are any.
        serializer = UseCaseSerializer(use_cases, many=True)

        return Response(data=serializer.data, exception=Exception())


class SaveCustomMUO(APIView):

    PARAM_CWE_CODES = "cwes"
    PARAM_MISUSE_CASE = "muc"
    PARAM_USE_CASE = "uc"

    TEMPLATE_MISUSE_CASE = {
        "misuse_case_description": "",
        "misuse_case_primary_actor": "",
        "misuse_case_secondary_actor": "",
        "misuse_case_precondition": "",
        "misuse_case_flow_of_events": "",
        "misuse_case_postcondition": "",
        "misuse_case_assumption": "",
        "misuse_case_source": "",
    }
    TEMPLATE_USE_CASE = {
        "use_case_description": "",
        "use_case_primary_actor": "",
        "use_case_secondary_actor": "",
        "use_case_precondition": "",
        "use_case_flow_of_events": "",
        "use_case_postcondition": "",
        "use_case_assumption": "",
        "use_case_source": "",
        "osr_pattern_type": "",
        "osr": "",
    }

    @staticmethod
    def _check_all_sections_present(data_dict):
        sections_missing = []
        if SaveCustomMUO.PARAM_CWE_CODES not in data_dict:
            sections_missing.append(SaveCustomMUO.PARAM_CWE_CODES)
        if SaveCustomMUO.PARAM_MISUSE_CASE not in data_dict:
            sections_missing.append(SaveCustomMUO.PARAM_MISUSE_CASE)
        if SaveCustomMUO.PARAM_USE_CASE not in data_dict:
            sections_missing.append(SaveCustomMUO.PARAM_USE_CASE)

        return sections_missing

    @staticmethod
    def _check_all_sections_mapping(data_dict):
        sections_wrong_type = []

        for key, value in data_dict.iteritems():
            if not isinstance(key, unicode) or not isinstance(value, unicode):
                sections_wrong_type.append(key)

        return sections_wrong_type

    @staticmethod
    def _validate_object_format_dict(obj):
        # The obj should be a dict.
        if not isinstance(obj, dict):
            return False
        # Now make sure the dict is a string -> string mapping.
        for item in obj.iteritems():
            if not isinstance(item[0], unicode) or not isinstance(item[1], unicode):
                return False
        return True

    @staticmethod
    def _validate_object_fields(object_template, object_dict):
        # Find the fields that are missing in the provided object.
        # It is OK even the field has an empty value, but it should not be missing.
        fields_missing = []
        for key in object_template.keys():
            if key not in object_dict:
                # If a field is not provided or its name is incorrectly spelled...
                fields_missing.append(key)

        return fields_missing

    @staticmethod
    def _form_err_msg_section_missing(sections_missing):
        return ("The following sections should be provided but missing: " +
                ("".join(section+", " for section in sections_missing)).rstrip(", "))

    @staticmethod
    def _form_err_msg_section_wrong_mapping(sections_wrong_mapping):
        return ("The following sections should be a mapping from string to string: " +
                ("".join(section+", " for section in sections_wrong_mapping)).rstrip(", "))

    @staticmethod
    def _form_err_msg_invalid_cwe_codes(cwe_codes_str):
        return ("CWE code list is malformed: \"" + cwe_codes_str + "\". " +
                "It should be a JSON string of a list of positive integers.")

    @staticmethod
    def _form_err_msg_wrong_format(object_name):
        return ("Incorrect format: " + object_name +
                " should be a JSON string of a dictionary that maps from string to string.")

    @staticmethod
    def _form_err_msg_fields_missing(object_name, fields_missing):
        return ("The following fields are missing from " + object_name + ": " +
                ("".join(field+", " for field in fields_missing).rstrip(", ")))

    @staticmethod
    def _form_err_msg_method_not_allowed():
        return "Use POST method for this REST API function."

    def get(self, request):
        # Because all the other REST API functions are implemented using GET,
        # we return an error message that tells the developer to use the POST method.
        return Response(data=self._form_err_msg_method_not_allowed(), status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request):
        # Validation: Check if all the sections have the (string -> string) mapping.
        sections_wrong_mapping = self._check_all_sections_mapping(request.data)
        if len(sections_wrong_mapping) > 0:
            err_msg = self._form_err_msg_section_wrong_mapping(sections_wrong_mapping)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Validation: Check if all the CWE codes, misuse case and use case(including
        # overlooked security requirement) are provided.
        # request.data is a dictionary.
        sections_missing = self._check_all_sections_present(request.data)
        # Now if sections_missing is not empty, we return the error.
        if len(sections_missing) > 0:
            err_msg = self._form_err_msg_section_missing(sections_missing)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Validation: Check if CWE codes are correct.
        cwe_codes_str = request.data[self.PARAM_CWE_CODES]
        try:
            cwe_code_list = json.loads(cwe_codes_str)
            if not isinstance(cwe_code_list, list):
                raise ValueError
        except ValueError:
            err_msg = self._form_err_msg_invalid_cwe_codes(cwe_codes_str)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Validation of misuse case.
        # 1). Check if it is in the correct format.
        misuse_case_str = request.data[self.PARAM_MISUSE_CASE]
        try:
            muc_dict = json.loads(misuse_case_str)
            if self._validate_object_format_dict(muc_dict) is False:
                raise ValueError
        except ValueError:
            err_msg = self._form_err_msg_wrong_format("misuse case")
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)
        # 2). Check if all required fields are present in misuse case.
        fields_missing = self._validate_object_fields(SaveCustomMUO.TEMPLATE_MISUSE_CASE, misuse_case_str)
        if len(fields_missing) > 0:
            err_msg = self._form_err_msg_fields_missing("misuse case", fields_missing)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Validation of use case.
        # 1). Check if it is in the correct format.
        use_case_str = request.data[self.PARAM_USE_CASE]
        try:
            uc_dict = json.loads(use_case_str)
            if self._validate_object_format_dict(uc_dict) is False:
                raise ValueError
        except ValueError:
            err_msg = self._form_err_msg_wrong_format("use case")
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)
        # 2). Check if all required fields are present in use case.
        fields_missing = self._validate_object_fields(SaveCustomMUO.TEMPLATE_USE_CASE, use_case_str)
        if len(fields_missing) > 0:
            err_msg = self._form_err_msg_fields_missing("use case", fields_missing)
            return Response(data=err_msg, status=status.HTTP_400_BAD_REQUEST)

        # Get the CWE code list.
        cwe_code_list = json.loads(cwe_codes_str)

        # Get the user.
        # Because by the time that this 'post' method is executed, the
        # user authentication had been done earlier so the user must be
        # an existent and valid one. There should be no exception.
        creator = User.objects.get(username=request.user.username)

        # Save the custom MUO.
        try:
            MUOContainer.create_custom_muo(cwe_ids=cwe_code_list,
                                           misusecase=muc_dict,
                                           usecase=uc_dict,
                                           created_by=creator)
        except Exception as e:
            return Response(data=e.message, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
