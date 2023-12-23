# -*- coding: utf-8 -*-

"""
Interface
*********

This module includes the base interface dedicated to the interaction with a Smart Plug.
"""

# ---------------------------------------- IMPORTS ----------------------------------------

from abc import ABC, abstractmethod
from importlib import import_module
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from lspm.exceptions import SmartPlugConnectionError, UnsupportedSmartPlugModel
from lspm.smartplug.credentials import PlugCredentials


# ---------------------------------------- CLASSES ----------------------------------------


class _FactorySmartPlugInterface:
    """
    The :class:`_FactorySmartPlugInterface` class is intended to give the :class:`SmartPlug` class
    the ability to act as a factory method.

    Concretely, it overrides the dunder method `__new__()` which then returns a subclass of
    :class:`SmartPlug` based on the argument `model`.

    This class is therefore not intended to be instantiated directly.
    """

    def __new__(cls: Type['SmartPlug'], model: str, address: str, account: str) -> 'SmartPlug':
        if cls is _FactorySmartPlugInterface:
            raise TypeError("Can't instantiate this class directly.")
        available_interfaces: List[Type['SmartPlug']] = cls._get_available_smart_plug_class_implementations()
        # model: str = model or cls._get_smart_plug_model(address)
        suitable_interface: Type['SmartPlug'] = cls._infer_suitable_smart_plug_class_implementation(
            available_interfaces, model
        )
        return super().__new__(suitable_interface)

    """
    CLASS METHODS
    """

    @classmethod
    def _dynamically_import_modules_containing_smart_plug_class_implementations(cls) -> None:
        """
        Dynamically imports modules from the `smartplug` subpackage.

        :return: None
        """
        current_module_path: Path = Path(__file__)
        current_package_path: Path = current_module_path.parent
        module_names: List[str] = [module_path.stem for module_path in current_package_path.glob('**/*.py')
                                   if module_path.name not in ['__init__.py', current_module_path.name]]
        for module_name in module_names:
            import_module(f'.{module_name}', package=__package__)

    @classmethod
    def _get_available_smart_plug_class_implementations(cls) -> List[Type['SmartPlug']]:
        """
        Returns a list of :class:`SmartPlug` subclasses currently implemented in the `smartplug` subpackage.

        :return: Direct subclasses of :class:`SmartPlug`.
        """
        cls._dynamically_import_modules_containing_smart_plug_class_implementations()
        return SmartPlug.__subclasses__()

    # @classmethod
    # def _get_smart_plug_model(cls, address: str) -> str:
    #     return ""  # TODO

    @classmethod
    def _infer_suitable_smart_plug_class_implementation(cls, available_interfaces: List[Type['SmartPlug']],
                                                        model: str) -> Type['SmartPlug']:
        """
        Infers the suitable :class:`SmartPlug` class implementation based on the provided `model`.

        :param List[Type['SmartPlug']] available_interfaces: list of :class:`SmartPlug` subclasses currently
                                                             implemented in the `smartplug` subpackage.
        :param str model: model name of the target Smart Plug.

        :return: Suitable :class:`SmartPlug` class implementation for the provided `model`.
        """
        model_names: List[str] = []
        for interface in available_interfaces:
            if not interface.supported_models():
                raise NotImplementedError(f"type object '{interface.__name__}' must specify a list of supported "
                                          f"Smart Plug models via the method 'supported_models()'")
            if model in interface.supported_models():
                return interface
            model_names.extend(interface.supported_models())
        raise UnsupportedSmartPlugModel(model, model_names)


class SmartPlug(ABC, _FactorySmartPlugInterface):
    """
    The :class:`SmartPlug` class is the interface dedicated to interacting with a Smart Plug.

    It has 2 major features:

    - it serves as a blueprint in order to implement concrete subclasses specific to
      each brand/model of Smart Plug
    - it acts as a factory method and can therefore be directly called to instantiate
      the appropriate subclass (based on the argument `model`)

    :param str model: model name of the Smart Plug. It is used by the class constructor to initialize
                      the appropriate subclass, i.e. the implementation allowing to interact
                      with this Smart Plug model.
    :param str address: IP address associated to the Smart Plug.
    :param Optional[PlugCredentials] account: credentials associated to the Smart Plug (if it has any).
    """

    def __init__(self, model: str, address: str, account: Optional[PlugCredentials]) -> None:
        self._model: str = model
        self._address: str = address
        self._account: Optional[PlugCredentials] = account
        try:
            self._plug = self._connect()
        except Exception:
            raise SmartPlugConnectionError(f"Failed to connect to the Smart Plug - "
                                           f"{self._address} is unreachable") from None

    def __repr__(self) -> str:
        return f"<SmartPlug [{self._model}] - IP Address: {self._address}>"

    """
    STATIC METHODS
    """

    @staticmethod
    @abstractmethod
    def supported_models() -> List[str]:
        """
        Returns a list of Smart Plug models supported by the current class.

        :return: List of supported Smart Plug model names.
        """
        pass

    """
    PROPERTIES
    """

    @property
    @abstractmethod
    def information(self) -> Dict[str, Any]:
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

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Returns the name of the Smart Plug.

        :return: Device name.
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
    def turn_off(self) -> None:
        """
        Sends the turn-off request to the Smart Plug.

        :return: None
        """
        pass

    @abstractmethod
    def turn_on(self) -> None:
        """
        Sends the turn-on request to the Smart Plug.

        :return: None
        """
        pass
