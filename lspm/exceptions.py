# -*- coding: utf-8 -*-

"""
Exceptions
**********

This module includes a set of classes to handle exceptions specific to the ``lspm`` package.
"""

# ---------------------------------------- IMPORTS ----------------------------------------

from typing import Dict, List


# ---------------------------------------- CLASSES ----------------------------------------

class LSPMException(Exception):
    """
    The :class:`LSPMException` is the base class for handling exceptions
    specific to the ``lspm`` package.
    """

    def __init__(self) -> None:
        self.error_msg: str = "LaptopSmartPowerManager Exception"

    def __str__(self) -> str:
        return self.error_msg


class CredentialsError(LSPMException):
    """
    The :class:`CredentialsError` is raised when there is any error related to
    the credentials associated to the Smart Plug.
    """

    error_types: Dict[str, str] = {
        "no_username": "No username to delete",
        "no_password": "No password to delete",
        "password_set_prematurely": "The username must be set before the password"
    }

    def __init__(self, error_type: str) -> None:
        self.error_msg: str = self.error_types.get(error_type)


class PowerSupplyStatusCheckError(LSPMException):
    """
    The :class:`PowerSupplyStatusCheckError` is raised when there is any error related to
    the retrieval of information about the power supply status of the computer.
    """

    error_types: Dict[str, str] = {
        "ac_power_cable": "Unable to know if the AC power cable is connected",
        "battery_state": "Unable to get information about battery state"
    }

    def __init__(self, error_type: str) -> None:
        self.error_msg: str = self.error_types.get(error_type)


class SmartPlugConnectionError(LSPMException):
    """
    The :class:`SmartPlugConnectionError` is raised when the Smart Plug is not reachable.
    """

    def __init__(self, error_msg: str) -> None:
        self.error_msg: str = error_msg


class SmartPlugInteractionError(LSPMException):
    """
    The :class:`SmartPlugInteractionError` is raised when interaction with
    the Smart Plug has been lost.
    """

    def __init__(self, action: str) -> None:
        self.error_msg: str = f"Unable to turn {action} the Smart Plug"


class UnsupportedSmartPlugModel(LSPMException):
    """
    The :class:`UnsupportedSmartPlugModel` is raised when the provided Smart Plug model
    is not supported by the currently implemented SmartPlug classes.
    """

    def __init__(self, model: str, supported_models: List[str]) -> None:
        self.error_msg: str = f"'{model}'.\nCurrently supported models are: {', '.join(supported_models)}"


class UnsupportedSystemError(LSPMException):
    """
    The :class:`UnsupportedSystemError` is raised when the Laptop Smart Power Manager is running on
    a system other than Windows, Linux or macOS.
    """

    def __init__(self, system_name: str) -> None:
        self.error_msg: str = (f"'{system_name}' system is not supported. "
                               f"Only Windows, Linux, and macOS are currently supported")
