import os
from pathlib import Path

from . import base
from . import local

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/26'

BASE_REMOTE = base.BaseRemote()
LOCAL = local.Local()

def is_surround_project():
    """Whether inside surround project root directory
    Check for the .surround folder
    """
    file_ = Path(".surround/config.yaml")
    if file_.exists():
        return True
    else:
        return False

def parse_remote_args(remote_parser, parsed_args):
    remote_name = parsed_args.name
    remote_path = parsed_args.path
    global_ = parsed_args.glob
    add = parsed_args.add
    verify = parsed_args.verify
    if add:
        if verify:
            print("error: unknown switch [-v VERIFY]")
            remote_parser.print_usage()
            print("[-a ADD] and [-v VERIFY] are mutually exclusive")
        else:
            if global_:
                # Make directory if not exists
                home = str(Path.home())
                os.makedirs(os.path.dirname(home + "/.surround/config.yaml"), exist_ok=True)
                if remote_name and remote_path:
                    BASE_REMOTE.write_config("remote", home + "/.surround/config.yaml", remote_name, remote_path)
                else:
                    print("error: supply remote name and path")
                    remote_parser.print_usage()
                    print("error: [-a ADD] [-n NAME] [-p PATH] are mutually inclusive")
            else:
                if is_surround_project():
                    if remote_name and remote_path:
                        BASE_REMOTE.write_config("remote", ".surround/config.yaml", remote_name, remote_path)
                    else:
                        print("error: supply remote name and path")
                        remote_parser.print_usage()
                        print("error: [-a ADD] [-n NAME] [-p PATH] are mutually inclusive")

                else:
                    print("error: not a surround project")
                    print("error: goto project root directory")
    else:
        if global_:
            remotes = BASE_REMOTE.read_all_from_global_config("remote")
            if remotes:
                for key, value in remotes.items():
                    if key:
                        if verify:
                            print(key + ": " + value)
                        else:
                            print(key)
            else:
                print("info: no global remote")
        else:
            if is_surround_project():
                remotes = BASE_REMOTE.read_all_from_local_config("remote")
                if remotes:
                    for key, value in remotes.items():
                        if key:
                            if verify:
                                print(key + ": " + value)
                            else:
                                print(key)
                else:
                    print("info: no local remote")
            else:
                print("error: not a surround project")
                print("error: goto project root directory")

def parse_add_args(parsed_args):
    if is_surround_project():
        remote = parsed_args.remote
        file_to_add = parsed_args.key
        message = LOCAL.add(remote, file_to_add)
        print(message)
    else:
        print("error: not a surround project")
        print("error: goto project root directory")

def parse_pull_args(parsed_args):
    if is_surround_project():
        remote = BASE_REMOTE.read_from_config("remote", parsed_args.remote)
        if remote:
            key = parsed_args.key
            message = LOCAL.pull(parsed_args.remote, key)
            print(message)
        else:
            print("Supply remote to pull from")
    else:
        print("Not a surround project")
        print("Goto project root directory")

def parse_push_args(parsed_args):
    if is_surround_project():
        remote = BASE_REMOTE.read_from_config("remote", parsed_args.remote)
        if remote:
            key = parsed_args.key
            message = LOCAL.push(parsed_args.remote, key)
            print(message)
        else:
            print("Supply remote to push to")
    else:
        print("Not a surround project")
        print("Goto project root directory")
