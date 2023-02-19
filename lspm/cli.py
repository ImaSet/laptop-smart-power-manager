# -*- coding: utf-8 -*-

"""
CLI
***

Command Line Interface (CLI) of the Laptop Smart Power Manager (LSPM)
"""

# ---------------------------------------- IMPORTS ----------------------------------------

import re
import sys
import json
import argparse
import warnings

from time import sleep
from pathlib import Path

from lspm import LaptopSmartPowerManager, PlugCredentials, TapoP100
from lspm.exceptions import CredentialsError


# ---------------------------------------- METHODS ----------------------------------------

def lspm_command() -> None:
    """
    Command-line binding to ``lspm`` package main features.

    TODO sub command 'discover' to discover if any smart plug is available in the LAN ?
     (see https://github.com/python-kasa/python-kasa)

    :return: None
    """
    program_name = "lspm"
    description = "Command Line Interface for LSPM, the Laptop Smart Power Manager."

    global_parser = argparse.ArgumentParser(prog=program_name, description=description)
    subparsers = global_parser.add_subparsers(title="Actions", metavar="<action>")

    start_parser = subparsers.add_parser("start", help="Start the Laptop Smart Power Manager.")
    start_parser.set_defaults(action=_start)

    config_parser = subparsers.add_parser("config", help="Launch the Smart Plug configuration interface.")
    config_parser.add_argument("-a", "--address", help="Set or update the Smart Plug IP address.")
    config_parser.add_argument("-u", "--username", help="Set or update the username associated to the Smart Plug.")
    config_parser.add_argument("-p", "--password", help="Set or update the password associated to the Smart Plug.")
    config_parser.add_argument("-c", "--clear", help="Clear the Smart Plug configuration.", action="store_true",
                               default=None)
    config_parser.set_defaults(action=_configure_smart_plug)

    compile_parser = subparsers.add_parser("compile", help="Create an executable version of LSPM.")
    compile_parser.set_defaults(action=_compile)

    args = global_parser.parse_args(args=None if sys.argv[1:] else ['-h'])
    if args.action.__name__ in ['_start', '_compile']:
        args.action()
    else:
        args.action(args)


def __is_ip_address(string: str) -> bool:
    ipv4_address_pattern = r"^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\." \
                           r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\." \
                           r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\." \
                           r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    string = string if isinstance(string, str) else ""
    return True if re.match(ipv4_address_pattern, string) else False


def __get_smart_plug_config_data() -> dict:
    """
    Retrieves the configuration parameters of the Connected Socket.

    Some of these settings are saved in the 'smart_plug' file located at $HOME$/.lspm/
    If this file and/or the '.lspm' directory do not exist, they are then created.

    :return: Dictionary containing only Smart Plug parameters available
             and correctly stored on the current machine.
    """
    # Create Smart Plug config file if it doesn't exist
    lspm_config_dir = Path(Path.home(), '.lspm')
    smart_plug_config = Path(lspm_config_dir, 'smart_plug')
    if not lspm_config_dir.exists():
        lspm_config_dir.mkdir()
    if not smart_plug_config.exists():
        smart_plug_config.touch()
    # Get Smart Plug config file data
    with open(smart_plug_config, 'r') as f:
        try:
            config_data = json.load(f)
        except json.JSONDecodeError:
            config_data = dict()
    # Set Smart Plug config parameters
    config_params = dict()
    config_params["address"] = config_data.get("address") if __is_ip_address(config_data.get("address")) else None
    warnings.simplefilter('ignore')
    account = PlugCredentials()
    config_params["username"] = account.username
    config_params["password"] = account.password
    warnings.resetwarnings()
    return {param: value for param, value in config_params.items() if value is not None}


def _start() -> None:
    """
    Starts the Laptop Smart Power Manager.

    :return: None
    """
    config = __get_smart_plug_config_data()
    missing_config_data = False
    if not config.get("address"):
        print("Smart Plug IP Address not found. You must set it with "
              "the following command: lspm config -a ADDRESS")
        missing_config_data = True
    if not config.get("username"):
        print("Smart Plug IP associated username not found. You must set it with "
              "the following command: lspm config -u USERNAME")
        missing_config_data = True
    if not config.get("password"):
        print("Smart Plug IP associated password not found. You must set it with "
              "the following command: lspm config -p PASSWORD")
        missing_config_data = True
    if missing_config_data:
        return
    # Get Smart Plug credentials
    account = PlugCredentials()
    # Connect to Smart Plug
    smart_plug = TapoP100(config["address"], account)
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


def _configure_smart_plug(args: argparse.Namespace) -> None:
    """
    Saves settings for connecting to the Smart Plug.

    Sensitive settings such as credentials are securely stored on the system.
    Other parameters such as the IP address of the Smart Plug are saved
    in a file located at $HOME$/.lspm/smart_plug

    :param argparse.Namespace args: object holding attributes entered by the user.

    :return: None
    """
    account = PlugCredentials()
    address, username, password = args.address, args.username, args.password
    config = __get_smart_plug_config_data()
    if all(arg is None for arg in [args.address, args.username, args.password, args.clear]):
        try:
            if any(stored_info is not None for stored_info in
                   [config.get('address'), config.get('username'), config.get('password')]):
                update_info = input("Found existing configuration. This operation will erase the "
                                    "previous configuration. \nDo you wish to continue? [y/n] ")
                if update_info.lower() not in ('y', 'yes'):
                    print("Operation aborted.")
                    return
            attempt = 0
            while attempt < 3:
                address = input("Enter the Smart Plug IP Address: ")
                attempt += 1
                if __is_ip_address(address):
                    break
                elif attempt < 3:
                    print("Invalid IPv4 address, please try again.")
                else:
                    print("Invalid IPv4 address, operation aborted.")
                    return
            username = input("Enter a new username: ")
            password = input("Enter a new password: ")
        except KeyboardInterrupt:
            print("\nOperation aborted.")
    elif args.clear:
        smart_plug_config = Path(Path.home(), '.lspm', 'smart_plug')
        smart_plug_config.unlink(missing_ok=True)
        try:
            warnings.simplefilter('ignore')
            del account.password
            del account.username
        except CredentialsError:
            pass
        print("Smart Plug configuration cleared.")
        return
    # Set Smart Plug configuration parameters
    if address is not None:
        if not __is_ip_address(address):
            print("Invalid IPv4 address, operation aborted.")
            return
        smart_plug_config = Path(Path.home(), '.lspm', 'smart_plug')
        with open(smart_plug_config, 'r+') as f:
            try:
                config_data = json.load(f)
            except json.JSONDecodeError:
                config_data = dict()
            config_data.update(address=address)
            f.seek(0)
            json.dump(config_data, f)
            f.truncate()
    warnings.simplefilter('ignore')
    if username is not None:
        account.username = username
    if password is not None:
        account.password = password
    warnings.resetwarnings()


def _compile() -> None:
    """
    Generates an executable of the Laptop Smart Power Manager.

    :return: None
    """
    print("Work in progress...")  # TODO
