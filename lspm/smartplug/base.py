# -*- coding: utf-8 -*-

"""
Smart Plug
**********

This module includes the base class dedicated to the interaction with a Smart Plug.
"""

# ---------------------------------------- IMPORTS ----------------------------------------

from abc import ABC, abstractmethod
from typing import Any, Optional

from lspm.smartplug.credentials import PlugCredentials
from lspm.exceptions import SmartPlugConnectionError


# ----------------------------------------- CLASS -----------------------------------------

class SmartPlug(ABC):
    """
    The :class:`SmartPlug` abstracts out some common functionality
    that is used across all Smart Plugs.

    :param str address: IP address associated to the Smart Plug.
    :param Optional[PlugCredentials] account: credentials associated to the Smart Plug (if it has any).
    """

    def __init__(self, address: str, account: Optional[PlugCredentials]) -> None:
        self._address = address
        self._account = account
        try:
            self._plug = self._connect()
        except Exception:
            raise SmartPlugConnectionError(f"Failed to connect to the Smart Plug - "
                                           f"{self._address} is unreachable") from None

    def __str__(self) -> str:
        return f"<SmartPlug - IP Address: {self._address}>"

    """
    PROPERTIES
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the Smart Plug.

        :return: Device name.
        """
        pass

    @property
    @abstractmethod
    def information(self) -> dict:
        """
        Returns some metadata about the Smart Plug.

        :return: Metadata about the device.
        """
        pass

    @property
    @abstractmethod
    def is_on(self) -> bool:
        """
        Returns the state of the Smart Plug.

        :return: ``True`` if the device is switched on, ``False`` otherwise.
        """
        pass

    """
    PROTECTED METHODS
    """

    @abstractmethod
    def _connect(self) -> Any:
        """
        Sets a session with the Smart Plug.

        :return: Underlying object associated to the Smart Plug.
        """
        pass

    """
    PUBLIC METHODS
    """

    @abstractmethod
    def turn_on(self) -> None:
        """
        Sends the turn-on request to the Smart Plug.

        :return: None
        """
        pass

    @abstractmethod
    def turn_off(self) -> None:
        """
        Sends the turn-off request to the Smart Plug.

        :return: None
        """
        pass
