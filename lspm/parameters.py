# -*- coding: utf-8 -*-

"""
Parameters
**********

This module contains the main parameters that control how the Laptop Smart Power Manager runs.
"""

# Time interval (in seconds) between each battery status check.
# Defaults to 30 seconds
REFRESH_TIME = 30

# Maximum time to wait (in seconds) for the Smart Plug state change action to take effect.
# Defaults to 10 seconds
STATE_CHANGE_TIMEOUT = 10

# Percentage value equivalent to the low battery state.
# Defaults to 20% (it should not be less than 7% which is the default critical battery level)
BATTERY_LOW = 20

# Percentage value equivalent to the charged battery state.
# Defaults to 100%
BATTERY_HIGH = 100
