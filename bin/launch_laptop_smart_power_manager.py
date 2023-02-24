# -*- coding: utf-8 -*-

"""
Launch LSPM
***********

This script shows how to launch the Laptop Smart Power Manager.
"""

from time import sleep

from lspm import PlugCredentials, TapoPlug, LaptopSmartPowerManager


# Set Smart Plug IP Address
address = "192.168.X.X"
# Get Smart Plug credentials
account = PlugCredentials()

# Connect to Smart Plug
smart_plug = TapoPlug(address, account)

# Initialize the Laptop Smart Power Manager
laptop_smart_power_manager = LaptopSmartPowerManager(smart_plug, handle_exceptions_in_main_thread=True)
# Start the Laptop Smart Power Manager
laptop_smart_power_manager.start()
print("Laptop Smart Power Manager started correctly")
print("To stop it, press CTRL + C (on macOS, Command + .)")
# This loop stops as soon as an interrupt-related event (CTRL+C, system shutdown) appears
while laptop_smart_power_manager.is_running:
    sleep(.1)
# Wait until the Laptop Smart Power Manager terminates
laptop_smart_power_manager.join()
# If the Laptop Smart Power Manager thread raised an exception, raise it here in the main thread
if laptop_smart_power_manager.exception:
    raise laptop_smart_power_manager.exception
print("Laptop Smart Power Manager stopped successfully")
