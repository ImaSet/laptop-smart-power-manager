# -*- coding: utf-8 -*-

"""
Credentials
***********

This module contains the class intended to retrieve the credentials
needed to connect to the Smart Plug.
"""

# ---------------------------------------- IMPORTS ----------------------------------------

from warnings import warn
from typing import Optional

from keyring import get_password, set_password, delete_password
from keyring.errors import PasswordDeleteError

from lspm.exceptions import CredentialsError


# ----------------------------------------- CLASS -----------------------------------------

class PlugCredentials:
    """
    The :class:`PlugCredentials` allows to interact with the credentials of the Smart Plug
    securely stored in the computer.
    """

    def __init__(self):
        self.__app_id = "SmartPowerManager"
        self.__app_key = "PlugCredentials"

    def __str__(self):
        return "<PlugCredentials>"

    @property
    def username(self) -> Optional[str]:
        """
        Retrieves the username associated to the Smart Plug.
        Issues a warning if the username is not found.

        :return: Username associated with the Smart Plug or None.
        """
        username = get_password(self.__app_id, self.__app_key)
        if username is None:
            warn("No credentials found for the Smart Plug")
        return username

    @username.setter
    def username(self, value: str) -> None:
        """
        Sets or updates the username associated to the Smart Plug.

        :param str value: username to set.

        :return: None
        """
        old_username = get_password(self.__app_id, self.__app_key)
        if old_username is None:
            # Set the username
            set_password(self.__app_id, self.__app_key, value)
        else:
            # Retrieve the password value associated to the old username
            associated_password = get_password(self.__app_id, old_username)
            if associated_password is not None:
                # Delete the registered password associated to the old username
                del self.password
                # Set the new username
                set_password(self.__app_id, self.__app_key, value)
                # Reassign the password value to the 'password' attribute
                self.password = associated_password

    @username.deleter
    def username(self) -> None:
        """
        Deletes the username associated to the Smart Plug.
        Raises an error if no username is associated to the Smart Plug.

        :return: None
        """
        if self.password is not None:
            del self.password
        try:
            delete_password(self.__app_id, self.__app_key)
        except PasswordDeleteError:
            raise CredentialsError("no_username")

    @property
    def password(self) -> Optional[str]:
        """
        Retrieves the password associated to the Smart Plug.
        Issues a warning if the password is not found.

        :return: Password associated with the Smart Plug or None.
        """
        username = self.username
        password = get_password(self.__app_id, username)
        if username is not None and password is None:
            warn("No password found for the Smart Plug")
        return password

    @password.setter
    def password(self, value: str) -> None:
        """
        Sets or updates the password associated to the Smart Plug.

        :param str value: password to set.

        :return: None
        """
        if self.username is None:
            raise CredentialsError("password_set_prematurely")
        set_password(self.__app_id, self.username, value)

    @password.deleter
    def password(self) -> None:
        """
        Deletes the password associated to the Smart Plug.
        Raises an error if no password is associated to the Smart Plug.

        :return: None
        """
        try:
            delete_password(self.__app_id, self.username)
        except PasswordDeleteError:
            raise CredentialsError("no_password")
