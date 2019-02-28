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
    return file_.exists()

def add_remote_parser(sub_parser):
    remote_parser = sub_parser.add_parser('remote', help="Initialise a new remote")
    remote_parser.add_argument('-n', '--name', help="Name of the remote")
    remote_parser.add_argument('-p', '--path', help="Url of the remote")
    remote_parser.add_argument('-a', '--add', help="Used to add a remote", action='store_true')
    remote_parser.add_argument('-v', '--verbose', help="verbose remote", action='store_true')
    remote_parser.add_argument('--global', help="Used to specify a global remote", action='store_true', dest='glob')
    return remote_parser

def create_add_parser(sub_parser):
    add_parser = sub_parser.add_parser('add', help="Add file to remote")
    add_parser.add_argument('remote', help="remote to add to")
    add_parser.add_argument('key', help="name of file to add")

def add_pull_parser(sub_parser):
    pull_parser = sub_parser.add_parser('pull', help="Pull file from remote")
    pull_parser.add_argument('remote', help="remote to pull")
    pull_parser.add_argument('-k', '--key', help="key of file to pull (from .surround/config.yaml)")

def add_push_parser(sub_parser):
    push_parser = sub_parser.add_parser('push', help="Push file to remote")
    push_parser.add_argument('remote', help="remote to push")
    push_parser.add_argument('-k', '--key', help="key of file to push (from .surround/config.yaml)")

def add_list_parser(sub_parser):
    list_parser = sub_parser.add_parser('list', help="List file in remote")
    list_parser.add_argument('remote', help="remote to list")

def write_remote_config(parsed_args, remote_parser, file_to_write):
    remote_name = parsed_args.name
    remote_path = parsed_args.path

    if remote_name and remote_path:
        BASE_REMOTE.write_config("remote", file_to_write, remote_name, remote_path)
    else:
        print("error: supply remote name and path")
        remote_parser.print_usage()
        print("error: [-a ADD] [-n NAME] [-p PATH] are mutually inclusive")

def add_remote(remote_parser, parsed_args):
    verbose = parsed_args.verbose
    global_ = parsed_args.glob

    if verbose:
        print("error: unknown switch [-v verbose]")
        remote_parser.print_usage()
        print("[-a ADD] and [-v verbose] are mutually exclusive")
    else:
        if global_:
            # Make directory if not exists
            home = str(Path.home())
            os.makedirs(os.path.dirname(home + "/.surround/config.yaml"), exist_ok=True)
            write_remote_config(parsed_args, remote_parser, home + "/.surround/config.yaml")
        else:
            if is_surround_project():
                write_remote_config(parsed_args, remote_parser, ".surround/config.yaml")
            else:
                print("error: not a surround project")
                print("error: goto project root directory")

def print_remote_info(parsed_args, remotes):
    verbose = parsed_args.verbose

    if remotes:
        for key, value in remotes.items():
            if key:
                if verbose:
                    print(key + ": " + value)
                else:
                    print(key)
    else:
        print("info: no remote found")

def parse_remote_args(remote_parser, parsed_args):
    global_ = parsed_args.glob
    add = parsed_args.add

    if add:
        add_remote(remote_parser, parsed_args)
    else:
        if global_:
            remotes = BASE_REMOTE.read_all_from_global_config("remote")
            print_remote_info(parsed_args, remotes)
        else:
            if is_surround_project():
                remotes = BASE_REMOTE.read_all_from_local_config("remote")
                print_remote_info(parsed_args, remotes)
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
            print("error: supply remote to pull from")
    else:
        print("error: not a surround project")
        print("error: goto project root directory")

def parse_push_args(parsed_args):
    if is_surround_project():
        remote = BASE_REMOTE.read_from_config("remote", parsed_args.remote)
        if remote:
            key = parsed_args.key
            message = LOCAL.push(parsed_args.remote, key)
            print(message)
        else:
            print("error: supply remote to push to")
    else:
        print("error: not a surround project")
        print("error: goto project root directory")

def parse_list_args(parsed_args):
    project_name = BASE_REMOTE.read_from_local_config("project-info", "project-name")
    path_to_remote = BASE_REMOTE.read_from_config("remote", parsed_args.remote)
    path_to_remote_files = path_to_remote + "/" + project_name
    message = os.listdir(path_to_remote_files)
    print(message)
