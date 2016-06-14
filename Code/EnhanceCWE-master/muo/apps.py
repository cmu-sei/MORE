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
from django.apps import AppConfig

class MUOConfig(AppConfig):
    name = 'muo'
    verbose_name = "MUO (Misuse Cases, Use Cases & Overlooked Security Requirements)"

    def ready(self):
        # Importing autocomplete_registry only after models are ready and app is fully loaded
        import autocomplete_registry
