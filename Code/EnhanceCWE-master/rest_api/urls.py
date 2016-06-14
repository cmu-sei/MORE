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
from django.conf.urls import url
from rest_api import views

urlpatterns = [
    url(r'^cwe/text_related$', views.CWERelatedList.as_view(), name="restapi_CWETextRelated"),
    url(r'^cwe/all$', views.CWEAllList.as_view(), name="restapi_CWEAll"),
    url(r'^cwe/search_str', views.CWESearchSingleString.as_view(), name="restapi_CWESearchSingleString"),
    url(r'^misuse_case/cwe_related$', views.MisuseCaseRelated.as_view(), name="restapi_MisuseCase_CWERelated"),
    url(r'^use_case/misuse_case_related$', views.UseCaseRelated.as_view(), name="restapi_UseCase_MisuseCaseRelated"),
    url(r'^custom_muo/save$', views.SaveCustomMUO.as_view(), name="restapi_CustomMUO_Create"),
]
