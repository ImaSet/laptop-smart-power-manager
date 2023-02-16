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


sys.path.append(r'D:\Documents\Projets\SmartPowerManager')  # TODO remove
from lspm import LaptopSmartPowerManager, PlugCredentials, TapoP100
from lspm.exceptions import CredentialsError


# ---------------------------------------- METHODS ----------------------------------------

def lspm_command() -> None:
    """
    Command-line biding to ``lspm`` package main features.

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
    args.action(args)


def __get_smart_plug_config_data() -> dict:
    """
    TODO

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
    config_params["address"] = config_data.get("address")
    config_params["model"] = config_data.get("model")
    warnings.simplefilter('ignore')
    account = PlugCredentials()
    config_params["username"] = account.username
    config_params["password"] = account.password
    warnings.resetwarnings()
    return {param: value for param, value in config_params.items() if value is not None}


def _start(args: argparse.Namespace) -> None:
    """
    TODO

    :param argparse.Namespace args:

    :return: None
    """
    # Get Smart Plug IP Address
    smart_plug_config = Path(Path.home(), '.lspm', 'smart_plug')
    if not smart_plug_config.exists():
        raise SystemExit("No config file found. You must set the IP address of the Smart Plug")
    with open(smart_plug_config, 'r') as f:
        address = f.read().strip()
    # Get Smart Plug model
    # TODO get Smart Plug child class name from config file
    # Get Smart Plug credentials
    account = PlugCredentials()
    # Connect to Smart Plug
    smart_plug = TapoP100(address, account)
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
    TODO

    :param argparse.Namespace args:

    :return: None
    """
    lspm_config_dir = Path(Path.home(), '.lspm')
    smart_plug_config = Path(lspm_config_dir, 'smart_plug')
    if not lspm_config_dir.exists():
        lspm_config_dir.mkdir()
    if not smart_plug_config.exists():
        stored_address = None
        smart_plug_config.touch()  # TODO faire un fichier JSON
    else:
        with open(smart_plug_config, 'r') as f:
            config_data = f.readlines()
        stored_address = config_data[0] if len(config_data) > 0 else ""
        ipv4_address_pattern = r"^(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\." \
                               r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\." \
                               r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\." \
                               r"(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        if not re.match(ipv4_address_pattern, stored_address):
            stored_address = None
    warnings.simplefilter('ignore')
    account = PlugCredentials()
    stored_username, stored_password = account.username, account.password
    warnings.resetwarnings()
    if all(arg is None for arg in [args.address, args.username, args.password, args.clear]):
        try:
            if any(stored_info is not None for stored_info in [stored_address, stored_username, stored_password]):
                update_info = input("Found existing configuration. This operation will erase the "
                                    "previous configuration. \nDo you wish to continue? [y/n] ")
                if update_info.lower() not in ('y', 'yes'):
                    print("Operation aborted.")
                    return
            address = input("Enter the Smart Plug IP Address: ")
            # TODO Enter the Smart Plug model [TapoP100/Other]:
            username = input("Enter a new username: ")
            password = input("Enter a new password: ")
            print(address, username, password)
        except KeyboardInterrupt:
            print("\nOperation aborted.")
    elif args.clear:
        print("Clear config!")
        # smart_plug_config.unlink(missing_ok=True)
        # try:
        #     del account.password
        #     del account.username
        # except CredentialsError:
        #     pass
    else:
        if args.address is not None:
            print(args.address)
        if args.username is not None:
            print(args.username)
            # account.username = args.username
        if args.password is not None:
            print(args.password)
            # account.password = args.password


def _compile(args: argparse.Namespace) -> None:
    """
    TODO

    :param argparse.Namespace args:

    :return: None
    """
    print("Compile!")


# ----------------------------------------- MAIN ------------------------------------------

if __name__ == '__main__':
    # lspm_command()
    print(__get_smart_plug_config_data())
