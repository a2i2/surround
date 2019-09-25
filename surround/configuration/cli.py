import os
import argparse

from pathlib import Path

import yaml

from ..config import Config

REQUIRED_CONFIG = {
    "user.name": "Enter your name (user.name): ",
    "user.email": "Enter your email (user.email): "
}

DEFAULT_CONFIG = {
    "experiment.url": os.path.join(str(Path.home()), ".experiments", "local"),
    "experiment.location.local": os.path.join(str(Path.home()), ".experiments", "local"),
    "experiment.location.shared": os.path.join(str(Path.home()), ".experiments", "shared")
}

def get_parser():
    parser = argparse.ArgumentParser(prog="config", description="Surround Configuration Tool")

    parser.add_argument("key", help="The key of the configuration property", nargs="?")
    parser.add_argument("value", help="The value of the configuration property", nargs="?")
    parser.add_argument("-l", "--local", action="store_true", help="Set configuration to local config file")

    return parser

def write_config_to_file(config, filepath):
    data = config.get_dict()
    with open(filepath, "w+") as f:
        yaml.safe_dump(data, f)

def generate_data(data, keys, value):
    if len(keys) == 1:
        data[keys[0]] = value
    else:
        if keys[0] not in data:
            data[keys[0]] = {}
        generate_data(data[keys[0]], keys[1:], value)

def set_property(path, value, config, config_path, is_local):
    keys = path.split(".")

    data = {}
    generate_data(data, keys, value)

    config.read_from_dict(data)
    write_config_to_file(config, config_path)

    if is_local:
        print("info: successfully set property %s to %s in local configuration" % (path, value))
    else:
        print("info: successfully set property %s to %s in global configuration" % (path, value))

def update_required_fields(config, config_path, answers=None, verbose=True):
    data = {}

    # Ask the user to fill in the required fields
    for key, prompt in REQUIRED_CONFIG.items():
        if not config.get_path(key):
            if answers and key in answers:
                generate_data(data, key.split("."), answers[key])
            else:
                value = input(prompt)
                generate_data(data, key.split("."), value)

    # Ensure default values are in the config
    for key, value in DEFAULT_CONFIG.items():
        if not config.get_path(key):
            generate_data(data, key.split("."), value)

    if data:
        # Save the answers to the global config
        config.read_from_dict(data)
        write_config_to_file(config, config_path)

        if verbose:
            print("info: successfully updated the global configuration!")

def execute_tool(parser, args):
    if not args.local:
        # Get the global configuration path (in ~/.surround/config.yaml)
        config_path = os.path.join(str(Path.home()), ".surround", "config.yaml")
    else:
        # Get the local configuration path (using the auto load feature)
        config = Config(auto_load=True)

        if config.get_path("project_root"):
            config_path = os.path.join(config["project_root"], ".surround", "config.yaml")
        else:
            print("error: not currently in a Surround project!")
            return

    # Create the config file if it doesn't exist
    if not os.path.exists(config_path):
        os.mkdir(os.path.dirname(config_path))
        open(config_path, "w+").close()

    config = Config(auto_load=False)
    config.read_config_files([config_path])

    # Set property and save to the config file
    if args.key and args.value:
        set_property(args.key, args.value, config, config_path, args.local)
    elif args.local:
        print("error: no configuration property and value specified!")
    else:
        update_required_fields(config, config_path)
