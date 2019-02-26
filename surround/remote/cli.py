import os
from pathlib import Path

from . import base

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/26'

base_class = base.BaseRemote()

def is_surround_project():
    """Whether inside surround project root directory
    Check for the .surround folder
    """
    file_ = Path(".surround/config.yaml")
    if file_.exists():
        return True
    else:
        return False

def parse_remote_args(parsed_args):
    remote_name = parsed_args.name
    remote_path = parsed_args.path
    global_ = parsed_args.glob
    add = parsed_args.add
    verify = parsed_args.verify
    if add:
        if global_:
            # Make directory if not exists
            home = str(Path.home())
            os.makedirs(os.path.dirname(home + "/.surround/config.yaml"), exist_ok=True)
            if remote_name and remote_path:
                base_class.write_config("remote", home + "/.surround/config.yaml", remote_name, remote_path)
            else:
                print("Supply remote name and path")
        else:
            if is_surround_project():
                if remote_name and remote_path:
                    base_class.write_config("remote", ".surround/config.yaml", remote_name, remote_path)
                else:
                    print("Supply remote name and path")
            else:
                print("Not a surround project")
                print("Goto project root directory")
    else:
        if global_:
            remotes = base_class.read_all_from_global_config("remote")
            for key, value in remotes.items():
                if key:
                    if verify:
                        print(key + ": " + value)
                    else:
                        print(key)
        else:
            if is_surround_project():
                remotes = base_class.read_all_from_local_config("remote")
                for key, value in remotes.items():
                    if key:
                        if verify:
                            print(key + ": " + value)
                        else:
                            print(key)
            else:
                print("Not a surround project")
                print("Goto project root directory")

def create_main_remote_group(parser_to_add_to):
    append_view_remote_group_to_main_remote(parser_to_add_to)

def append_view_remote_group_to_main_remote(remote_parser):
    view_remote_group = remote_parser.add_argument_group('view-remote-group')
    view_remote_group.add_argument('--global', help="Used to specify a global remote", action='store_true', dest='glob')
    view_remote_group.add_argument('-v', '--verify', help="Verify remote", action='store_true')
