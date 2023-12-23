# -*- coding: utf-8 -*-

"""
Laptop Smart Power Manager
**************************

This module contains the main class intended to monitor the battery status of
the computer and manage its power supply.
"""

# ---------------------------------------- IMPORTS ----------------------------------------

import logging

from typing import Tuple
from threading import Thread, Event, Timer
from time import sleep

from psutil import sensors_battery

from lspm.smartplug import SmartPlug
from lspm.parameters import REFRESH_TIME, STATE_CHANGE_TIMEOUT, BATTERY_LOW, BATTERY_HIGH
from lspm.exceptions import SmartPlugConnectionError, SmartPlugInteractionError, PowerSupplyStatusCheckError
from lspm.interrupt_event_handler import set_interrupt_event_handler
from lspm.logger import set_logging


# ----------------------------------------- CLASS -----------------------------------------

class LaptopSmartPowerManager(Thread):
    """
    The :class:`LaptopSmartPowerManager` is intended to monitor the battery status of
    the laptop and manage its power supply.

    :param SmartPlug smart_plug: the SmartPlug object with which the LaptopSmartPowerManager interacts.
    :param bool handle_exceptions_in_main_thread: defaults to ``False``. Set this parameter to ``True`` if
           exceptions raised in this thread are going to be handled from the main thread. In this case,
           all exceptions thrown in that thread are ignored, and throwing any exception causes that
           thread to terminate silently.
    """

    def __init__(self, smart_plug: SmartPlug, handle_exceptions_in_main_thread: bool = False) -> None:
        Thread.__init__(self)
        set_logging()
        self.__logger = logging.getLogger("lspm")
        self.__logger.info("Initializing the Laptop Smart Power Manager")
        self.exception = None
        self.__handle_exceptions_in_main_thread = handle_exceptions_in_main_thread
        self.__finished = Event()
        self.__connection_lost = False
        self.__smart_plug = smart_plug
        self.__check_connection_to_smart_plug()
        self.__smart_plug.turn_off()
        self.__logger.debug("Sent turn-off request to the Smart Plug")
        self.__check_smart_plug_state("off")
        self.__manage_power_supply()
        self.__interrupt_event_handler = set_interrupt_event_handler(exit_function=self.stop)

    """
    PROPERTIES
    """

    @property
    def is_running(self) -> bool:
        """
        Indicates whether the LaptopSmartPowerManager thread is alive.
        At the same time, checks if any system events
        have appeared.

        :return: ``True`` if the LaptopSmartPowerManager thread is alive, ``False`` otherwise.
        """
        self.__interrupt_event_handler.check_events()
        return True if self.is_alive() else False

    """
    PRIVATE METHODS
    """

    def __check_connection_to_smart_plug(self) -> None:
        """
        Checks that the Smart Plug is still reachable.

        :raises SmartPlugConnectionError: if the connection to the Smart Plug is lost.

        :return: None
        """
        try:
            _ = self.__smart_plug.is_on
        except Exception:
            self.__connection_lost = True
            self.stop()
            raise SmartPlugConnectionError("Connection lost to the Smart Plug") from None

    def __check_smart_plug_state(self, state: str) -> None:
        """
        Checks that the state of the Smart Plug matches that indicated by ``state`` ("on" or "off").

        :raises SmartPlugInteractionError: if the state of the Smart Plug has not changed to
                that indicated by ``state`` after the time expressed by
                ``STATE_CHANGE_TIMEOUT`` parameter.

        :param str state: ``on`` if the Smart Plug is supposed to be on, ``off`` otherwise.

        :return: None
        """
        def interaction_lost():
            state_changed.set()
            self.__connection_lost = True
            self.stop()
            raise SmartPlugInteractionError(state)

        state_changed = Event()
        expected_state = True if state.lower() == "on" else False
        timeout = Timer(STATE_CHANGE_TIMEOUT, interaction_lost)
        timeout.start()
        while not state_changed.is_set():
            if self.__smart_plug.is_on is expected_state:
                state_changed.set()
            sleep(.1)
        timeout.cancel()
        self.__logger.info(f"Smart Plug status check: turned {state.upper()}")

    @staticmethod
    def __get_battery_state() -> Tuple[int, bool]:
        """
        Retrieves some information about the current state of the computer's battery.

        :return: Battery power left as a percentage and boolean indicating if
                 the AC power cable is connected.
        """
        battery = sensors_battery()
        if battery is not None:
            if battery.power_plugged is None:
                raise PowerSupplyStatusCheckError("ac_power_cable")
            else:
                return battery.percent, battery.power_plugged
        else:
            raise PowerSupplyStatusCheckError("battery_state")

    def __manage_power_supply(self) -> None:
        """
        Turns on or off the Smart Plug to which the AC power cable of the computer
        is connected depending on the level of battery charge.

        :return: None
        """
        battery_level, power_plugged = self.__get_battery_state()
        self.__logger.debug(f"Battery level: {battery_level}% - Power plugged: {'Yes' if power_plugged else 'No'}")
        if not power_plugged and battery_level < BATTERY_LOW:
            self.__smart_plug.turn_on()
            self.__logger.debug("Sent turn-on request to the Smart Plug")
            self.__check_smart_plug_state("on")
        elif power_plugged and battery_level >= BATTERY_HIGH:
            self.__smart_plug.turn_off()
            self.__logger.debug("Sent turn-off request to the Smart Plug")
            self.__check_smart_plug_state("off")

    """
    PUBLIC METHODS
    """

    def run(self) -> None:
        """
        Checks the battery status of the computer at given time interval
        and manages its power supply if needed.

        :return: None
        """
        self.__logger.info("Laptop Smart Power Manager started correctly")
        while True:
            self.__finished.wait(REFRESH_TIME)
            if not self.__finished.is_set():
                try:
                    self.__check_connection_to_smart_plug()
                    self.__manage_power_supply()
                except Exception as e:
                    self.__logger.error(str(e))
                    if self.__handle_exceptions_in_main_thread:
                        self.exception = e
                    else:
                        raise e
            else:
                break

    def stop(self) -> None:
        """
        Stops the computer's power supply monitoring and management thread.

        :return: None
        """
        self.__finished.set()
        if not self.__connection_lost:
            self.__smart_plug.turn_off()
            self.__logger.info("Laptop Smart Power Manager stopped successfully")
