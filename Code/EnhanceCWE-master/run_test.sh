#!/usr/bin/env bash

echo "This script tests the project."

# Set the sum of return values to 0.
ret_sum=0
# Set the return value of the last command to 0.
last_ret=0

# Run all the tests in the project.
python manage.py test --settings=EnhancedCWE.settings_travis
# Get the return value of last command.
last_ret=$?
# Calculate the sum of all the return values so far.
ret_sum=$(($ret_sum+$last_ret))

# Exit with the ret_sum.
# Travis thinks the command is successful when its return value is zero,
# and unsuccessful when not zero. Therefore, the ret_sum will not be zero
# as long as any of the test execution commands fails.
# If we don't calculate the sum of return values, the last successful
# command may override the failures of the previous commands.
exit $ret_sum
