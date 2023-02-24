# -*- coding: utf-8 -*-

"""
Exceptions
**********

This module includes a set of classes to handle exceptions specific to the ``lspm`` package.
"""


# ---------------------------------------- CLASSES ----------------------------------------

class LSPMException(Exception):
    """
    The :class:`LSPMException` is the base class for handling exceptions
    specific to the ``lspm`` package.
    """

    def __init__(self) -> None:
        self.error_msg = "LaptopSmartPowerManager Exception"

    def __str__(self) -> str:
        return self.error_msg


class CredentialsError(LSPMException):
    """
    The :class:`CredentialsError` is raised when there is any error related to
    the credentials associated to the Smart Plug.
    """

    error_types = {
        "no_username": "No username to delete",
        "no_password": "No password to delete",
        "password_set_prematurely": "The username must be set before the password"
    }

    def __init__(self, error_type: str) -> None:
        self.error_msg = self.error_types.get(error_type)


class SmartPlugConnectionError(LSPMException):
    """
    The :class:`SmartPlugConnectionError` is raised when the Smart Plug is not reachable.
    """

    def __init__(self, error_msg: str) -> None:
        self.error_msg = error_msg


class SmartPlugInteractionError(LSPMException):
    """
    The :class:`SmartPlugInteractionError` is raised when interaction with
    the Smart Plug has been lost.
    """

    def __init__(self, action: str) -> None:
        self.error_msg = f"Unable to turn {action} the Smart Plug"


class PowerSupplyStatusCheckError(LSPMException):
    """
    The :class:`PowerSupplyStatusCheckError` is raised when there is any error related to
    the retrieval of information about the power supply status of the computer.
    """

    error_types = {
        "ac_power_cable": "Unable to know if the AC power cable is connected",
        "battery_state": "Unable to get information about battery state"
    }

    def __init__(self, error_type: str) -> None:
        self.error_msg = self.error_types.get(error_type)


class UnsupportedSystemError(LSPMException):
    """
    The :class:`UnsupportedSystemError` is raised when the Laptop Smart Power Manager is running on
    a system other than Windows, Linux or macOS.
    """

    def __init__(self, system_name: str) -> None:
        self.error_msg = f"'{system_name}' system is not supported. " \
                         f"Only Windows, Linux, and macOS are currently supported"
