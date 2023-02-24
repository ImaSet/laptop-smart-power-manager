# -*- coding: utf-8 -*-

"""
Tapo Plug
*********

This module includes the class dedicated to the interaction with TP-Link 'Tapo' Smart Plugs.
"""

# ---------------------------------------- IMPORTS ----------------------------------------

from PyP100.PyP100 import P100

from .base import SmartPlug


# ----------------------------------------- CLASS -----------------------------------------


class TapoPlug(SmartPlug):
    """
    The :class:`TapoPlug` contains a set of methods allowing to interact
    with TP-Link 'Tapo' Smart Plugs.
    """

    """
    PROPERTIES
    """

    @property
    def name(self) -> str:
        """
        Returns the name of the Smart Plug.

        :return: Device name.
        """
        return self._plug.getDeviceName()

    @property
    def information(self) -> dict:
        """
        Returns some metadata about the Smart Plug.

        :return: Metadata about the device.
        """
        return self._plug.getDeviceInfo()

    @property
    def is_on(self) -> bool:
        """
        Returns the state of the Smart Plug.

        :return: ``True`` if the device is switched on, ``False`` otherwise.
        """
        return self.information['result']["device_on"]

    """
    PROTECTED METHODS
    """

    def _connect(self) -> P100:
        """
        Sets a session with the Smart Plug.

        :return: Underlying object associated to the Smart Plug.
        """
        plug = P100(self._address, self._account.username, self._account.password)
        # Create the cookie required for further methods
        plug.handshake()
        # Send credentials to the plug then create AES Key and IV for further methods
        plug.login()
        return plug

    """
    PUBLIC METHODS
    """

    def turn_on(self) -> None:
        """
        Sends the turn-on request to the Smart Plug.

        :return: None
        """
        self._plug.turnOn()

    def turn_off(self) -> None:
        """
        Sends the turn-off request to the Smart Plug.

        :return: None
        """
        self._plug.turnOff()
