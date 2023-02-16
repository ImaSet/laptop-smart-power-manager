# -*- coding: utf-8 -*-

"""
Interrupt Event Handlers
************************

This module contains the classes intended to handle events leading to
the interruption of the Laptop Smart Power Manager.
"""

# ---------------------------------------- IMPORTS ----------------------------------------

import platform

from abc import ABC, abstractmethod
from typing import Callable, Any
from signal import signal, SIGINT, SIGTERM

from win32api import GetModuleHandle
from win32gui import WNDCLASS, RegisterClass, CreateWindowEx, PumpWaitingMessages
from win32con import WM_QUERYENDSESSION, WS_EX_LEFT, CW_USEDEFAULT

from lspm.exceptions import UnsupportedSystemError


# ---------------------------------------- METHODS ----------------------------------------

def set_interrupt_event_handler(exit_function: Callable, args: Any = None,
                                kwargs: Any = None) -> 'InterruptEventHandler':
    """
    Initializes the appropriate InterruptEventHandler depending on the system (Windows,
    Linux or macOS) on which the Smart Power Manager is running.

    :param Callable exit_function: function executed when the Windows shutdown event is caught.
    :param Any args: non-keyword arguments of ``exit_function``.
    :param Any kwargs: keyword arguments of ``exit_function``.

    :return: an InterruptEventHandler object specific to the system on which
             the Smart Power Manager is running.
    """
    system_name = platform.system()
    if system_name == "Windows":
        return WindowsInterruptEventHandler(exit_function, args, kwargs)
    elif system_name == "Linux":
        return LinuxInterruptEventHandler(exit_function, args, kwargs)
    elif system_name == "Darwin":
        return MacOSInterruptEventHandler(exit_function, args, kwargs)
    else:
        raise UnsupportedSystemError(system_name)


# ---------------------------------------- CLASSES ----------------------------------------

class InterruptEventHandler(ABC):
    """
    The :class:`InterruptEventHandler` abstracts out some common functionality
    that is used across all Interrupt Event Handlers.

    :param Callable exit_function: function executed when the Windows shutdown event is caught.
    :param Any args: non-keyword arguments of ``exit_function``.
    :param Any kwargs: keyword arguments of ``exit_function``.
    """

    def __init__(self, exit_function: Callable, args: Any = None, kwargs: Any = None):
        self._exit_function = exit_function
        self._args = args if args is not None else []
        self._kwargs = kwargs if kwargs is not None else {}
        self._set_keyboard_interrupt_event_handler()
        self._set_shutdown_event_handler()

    """
    PROTECTED METHODS
    """

    def _set_keyboard_interrupt_event_handler(self) -> None:
        """
        Sets the handler to catch the "keyboard interrupt" signal (CTRL + C).
        When this event is caught, the method associated with
        the ``exit_function`` argument is run.

        :return: None
        """
        signal(SIGINT, lambda signum, frame: self._exit_function(*self._args, **self._kwargs))

    @abstractmethod
    def _set_shutdown_event_handler(self) -> None:
        """
        Sets a platform-specific event handler that can react to the system shutdown event.
        When this event is caught, the method associated with
        the ``exit_function`` argument is run.

        :return: None
        """
        pass

    """
    PUBLIC METHODS
    """

    @abstractmethod
    def check_events(self) -> None:
        """
        Pumps all waiting events for the current thread.

        :return: None
        """
        pass


class WindowsInterruptEventHandler(InterruptEventHandler):
    """
    The :class:`InterruptEventHandler` is intended to handle Windows-specific events
    leading to the interruption of the Smart Power Manager.
    """

    def _set_shutdown_event_handler(self) -> None:
        """
        Initializes a hidden *Microsoft Windows* window allowing to react to the Windows Shutdown Event.
        When this event is caught, the method associated with
        the ``exit_function`` argument is run.

        :return: None
        """
        handle_instance = GetModuleHandle(None)
        window_class = WNDCLASS()
        window_class.hInstance = handle_instance
        window_class.lpszClassName = "MessageHandlerWindowClass"
        window_class.lpfnWndProc = {
            WM_QUERYENDSESSION: lambda *params: self._exit_function(*self._args, **self._kwargs),
        }
        message_handler_window_class = RegisterClass(window_class)
        CreateWindowEx(WS_EX_LEFT,
                       message_handler_window_class,
                       "MessageHandlerWindow",
                       0,
                       0,
                       0,
                       CW_USEDEFAULT,
                       CW_USEDEFAULT,
                       0,
                       0,
                       handle_instance,
                       None)

    def check_events(self) -> None:
        """
        Pumps all waiting events for the current thread.

        :return: None
        """
        PumpWaitingMessages()


class LinuxInterruptEventHandler(InterruptEventHandler):
    """
    TODO NOT TESTED !
    The :class:`InterruptEventHandler` is intended to handle Linux-specific events
    leading to the interruption of the Smart Power Manager.
    """

    def _set_shutdown_event_handler(self) -> None:
        """
        Sets an event handler that can react to the system shutdown event.
        When this event is caught, the method associated with
        the ``exit_function`` argument is run.

        :return: None
        """
        signal(SIGTERM, lambda signum, frame: self._exit_function(*self._args, **self._kwargs))

    def check_events(self) -> None:
        """
        This method is not needed for Linux-based systems.

        :return: None
        """
        pass


class MacOSInterruptEventHandler(InterruptEventHandler):
    """
    TODO NOT TESTED !
    The :class:`InterruptEventHandler` is intended to handle macOS-specific events
    leading to the interruption of the Smart Power Manager.
    """

    def _set_shutdown_event_handler(self) -> None:
        """
        Sets an event handler that can react to the system shutdown event.
        When this event is caught, the method associated with
        the ``exit_function`` argument is run.

        :return: None
        """
        signal(SIGTERM, lambda signum, frame: self._exit_function(*self._args, **self._kwargs))

    def check_events(self) -> None:
        """
        This method is not needed for Mac OS-based systems.

        :return: None
        """
        pass
