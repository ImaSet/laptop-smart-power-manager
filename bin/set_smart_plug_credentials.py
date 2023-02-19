# -*- coding: utf-8 -*-

"""
Set Smart Plug Credentials
**************************

This script shows how to set credentials associated with the Smart Plug.
"""

from lspm import PlugCredentials


# Initialize the object holding the Smart Plug credentials
account = PlugCredentials()

# Set the username and password
account.username = "YOUR_USERNAME"
account.password = "YOUR_PASSWORD"

print(f"Username: {account.username}")
print(f"Password: {account.password}")
