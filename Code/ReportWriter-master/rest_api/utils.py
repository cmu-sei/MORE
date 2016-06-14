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
import requests
from requests.exceptions import ConnectionError
from .models import *
import json


class rest_api:

    @staticmethod
    def get_url():
        '''
        Returns the URL of REST API server
        :return: A string containing the URL
        '''
        if RESTConfiguration.objects.exists():
            config = RESTConfiguration.objects.all()[0]
            return config.url
        else:
            return None

    @staticmethod
    def get_header():
        '''
        Creates a dictionary of the things to be passed in the REST requests header
        :return: A dictionary containing the API key
        '''
        if RESTConfiguration.objects.exists():
            config = RESTConfiguration.objects.all()[0]
            return {'Authorization': 'Token %s' % config.token}
        else:
            return {}

    @staticmethod
    def process_response(response):
        '''
        This method process the response for errors or success
        :param response: Response object that's been returned from the server
        :return: A dictionary containing the following three key-values:
         success: A boolean value representing whether request to the server was successful or not
         msg: A string containing a descriptive message about what happened with the request
         obj: Any additional object (generally the JSON object) if some data is to be returned to the caller.
        '''
        success = False
        msg = None
        obj = None
        if response.status_code == requests.codes.unauthorized:
            # Authentication Failure
            msg = 'Authentication Failure. All requests must be authenticated with a valid API Key. ' \
                  'Please contact the system administrator. Additional error details are: %s' % response.content
        elif response.status_code == requests.codes.bad:
            # Bad Request
            msg = 'There is something wrong in the request. Please check all your inputs correctly.' \
                  'Additional error details are: %s' % response.content
        elif response.status_code == requests.codes.server_error:
            # Server Error occurred.
            msg = 'Some error has occurred on the server. Please try after some time!' \
                  'Additional error details are: %s' % response.content
        elif response.status_code == requests.codes.ok:
            # Successful
            success = True
            msg = 'Success'
            if response.headers.get('content-type') == 'application/json':
                # If the response is of type JSON, set the obj
                obj = response.json()

        return {'success': success, 'msg': msg, 'obj': obj}

    @staticmethod
    def handle_server_connection_error():
        '''
        This method handles the server connection error
        :return: A dictionary containing the failure flag and error message
        '''
        return {'success': False, 'msg': 'Cannot connect to Enhanced CWE system', 'obj': None}

    @staticmethod
    def get_cwes_for_description(description):
        '''
        This method makes a REST call to Enhanced CWE system to get the related CWEs for the report description
        :param description: A string which is the description of the report
        :return: Returns a dictionary containing whether the request was successful or not. If the request was not
                 successful, the dictionary also contains the descriptive error message. If the request was successful,
                 the dictionary also contains the list of the CWEs returned from the Enhanced CWE application
        '''
        payload = {'text': description}
        url_string = '%s/cwe/text_related' % rest_api.get_url()
        try:
            response = requests.get(url_string, params=payload, headers=rest_api.get_header())
            return rest_api.process_response(response)
        except ConnectionError as e:
            return rest_api.handle_server_connection_error()

    @staticmethod
    def get_cwes_with_search_string(search_string, offset, limit):
        '''
        This method makes a REST call to Enhanced CWE system to search the cwe based on one of the following arguments:
        :param search_string: string to be searched in code and name
        :param offset: An offset value indicating the id of the CWE where to start search from
        :param limit: Limit indicating the maximum number of results to return
        :return: Returns a dictionary containing whether the request was successful or not. If the request was not
                 successful, the dictionary also contains the descriptive error message. If the request was successful,
                 the dictionary also contains the list of the CWEs returned from the Enhanced CWE application
        '''
        payload = {'search_str': search_string,
                   'offset': offset,
                   'limit': limit}
        url_string = '%s/cwe/search_str' % rest_api.get_url()
        try:
            response = requests.get(url_string, params=payload, headers=rest_api.get_header())
            return rest_api.process_response(response)
        except ConnectionError as e:
            return rest_api.handle_server_connection_error()

    @staticmethod
    def get_cwes(code, name_search_string, offset, limit):
        '''
        This method makes a REST call to Enhanced CWE system to search the cwe based on one of the following arguments:
        :param code: CWE code
        :param name_search_string: A string to search in the name of the CWEs
        :param offset: An offset value indicating the id of the CWE where to start search from
        :param limit: Limit indicating the maximum number of results to return
        :return: Returns a dictionary containing whether the request was successful or not. If the request was not
                 successful, the dictionary also contains the descriptive error message. If the request was successful,
                 the dictionary also contains the list of the CWEs returned from the Enhanced CWE application
        '''
        payload = {'code': code,
                   'name_contains': name_search_string,
                   'offset': offset,
                   'limit': limit}
        url_string = '%s/cwe/all' % rest_api.get_url()
        try:
            response = requests.get(url_string, params=payload, headers=rest_api.get_header())
            return rest_api.process_response(response)
        except ConnectionError as e:
            return rest_api.handle_server_connection_error()

    @staticmethod
    def get_misuse_cases(cwe_codes):
        '''
        This method makes a REST call to Enhanced CWE system to get the list of misuse cases related a list of CWEs
        :param cwe_codes: A comma separated string of CWE codes for which misuse cases are needed
        :return: Returns a dictionary containing whether the request was successful or not. If the request was not
                 successful, the dictionary also contains the descriptive error message. If the request was successful,
                 the dictionary also contains the list of the misuse cases returned from the Enhanced CWE application
        '''
        payload = {'cwes': str(cwe_codes)}
        url_string = '%s/misuse_case/cwe_related' % rest_api.get_url()
        try:
            response = requests.get(url_string, params=payload, headers=rest_api.get_header())
            return rest_api.process_response(response)
        except ConnectionError as e:
            return rest_api.handle_server_connection_error()

    @staticmethod
    def get_use_cases(misuse_case_ids):
        '''
        This method makes a REST call to Enhanced CWE system to get the list of use cases related a list of misuse cases
        :param misuse_case_ids: A comma separated string of Misuse case ids for which use cases are needed
        :return: Returns a dictionary containing whether the request was successful or not. If the request was not
                 successful, the dictionary also contains the descriptive error message. If the request was successful,
                 the dictionary also contains the list of the use cases returned from the Enhanced CWE application
        '''
        payload = {'misuse_cases': str(misuse_case_ids)}
        url_string = '%s/use_case/misuse_case_related' % rest_api.get_url()
        try:
            response = requests.get(url_string, params=payload, headers=rest_api.get_header())
            return rest_api.process_response(response)
        except ConnectionError as e:
            return rest_api.handle_server_connection_error()


    @staticmethod
    def save_muos_to_enhanced_cwe(cwe_codes, misuse_case, use_case):
        '''
        This method makes a REST call to Enhanced CWE system to save the misuse case, use case and overlooked security
        requirements to the Enhanced CWE system
        :param cwe_codes: A list of integers representing cwe codes
        :param misuse_case: A dictionary containing the misuse case fields
        :param use_case: A dictionary containing the use case fields
        :return: Returns a dictionary containing whether the request was successful or not. If the request was not
                 successful, the dictionary also contains the descriptive error message.
        '''
        payload = {'cwes': json.dumps(cwe_codes),
                   'muc': json.dumps(misuse_case),
                   'uc': json.dumps(use_case)}
        url_string = '%s/custom_muo/save' % rest_api.get_url()
        try:
            response = requests.post(url_string, data=payload, headers=rest_api.get_header())
            return rest_api.process_response(response)
        except ConnectionError as e:
            return rest_api.handle_server_connection_error()
