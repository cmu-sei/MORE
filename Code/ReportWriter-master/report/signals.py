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
from django.dispatch import Signal
''' This file contains a list of all the signals which can be invoked whenever required
These signals are handled by the report_mailer App
For the implementation of each of these signals, see the report_mailer app, signal_handlers.py file
To call these signal, invoke it as signal_name.send(sender="", feedback="")
'''

# Sent when the report is approved by the reviewer
report_accepted = Signal(providing_args=["instance"])

# Sent when the report is rejected by the reviewer
report_rejected = Signal(providing_args=["instance"])

# Sent when the report is submitted for review
report_submitted_review = Signal(providing_args=["instance"])

# Sent when the report is saved in the EnhancedCWE Application - Not tested
report_saved_enhancedCWEApplication = Signal(providing_args=["instance"])





