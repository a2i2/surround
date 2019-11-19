import os
from pathlib import Path

from . import base
from . import local

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/26'

BASE_REMOTE = base.BaseRemote()
LOCAL = local.Local()

def is_surround_project():
    """
    Checks whether inside a surround project folder.
    Check for the .surround folder.

    :return: whether we're in a surround project or not
    :rype: boolean
    """

    dir_ = get_project_root_from_current_dir()
    if dir_ is None:
        return False
    return True

def get_project_root_from_current_dir():
    """
    Returns the project root directory for the current project we're in.

    :return: path to the root of the project
    :rtype: string
    """

    return get_project_root(os.getcwd())

def get_project_root(current_directory):
    """
    Returns the project root directory for the project at the provided directory.

    :returns: path to the root of the project
    :rtype: string
    """

    home = str(Path.home())

    while True:
        list_ = os.listdir(current_directory)
        parent_directory = os.path.dirname(current_directory)
        if current_directory in (home, parent_directory):
            break
        if ".surround" in list_:
            return current_directory
        current_directory = parent_directory

def add_store_parser(sub_parser):
    """
    Adds a sub-parser for the main "store" sub-command to the parser provided.

    :param sub_parser: the parser to add to
    :type sub_parser: <class 'argparse.ArgumentParser'>
    :return: the parser added
    :rtype: <class 'argparse.ArgumentParser'>
    """

    store_parser = sub_parser.add_parser('store', help="Data remote storage tool")
    sub_parser = store_parser.add_subparsers(dest='sub_command', description="Must be called with one of the following commands")

    add_remote_parser(sub_parser)
    add_pull_parser(sub_parser)
    add_push_parser(sub_parser)
    add_list_parser(sub_parser)

    return store_parser

def add_remote_parser(sub_parser):
    """
    Adds a sub-parser for the "remote" sub-command to the parser provided.

    :param sub_parser: the parser to add to
    :type sub_parser: <class 'argparse.ArgumentParser'>
    :return: the parser added
    :rtype: <class 'argparse.ArgumentParser'>
    """

    remote_parser = sub_parser.add_parser('remote', help="Initialise a new remote")
    remote_parser.add_argument('-n', '--name', help="Name of the remote")
    remote_parser.add_argument('-u', '--url', help="Url of the remote")
    remote_parser.add_argument('-a', '--add', help="Used to add a remote", action='store_true')
    remote_parser.add_argument('-v', '--verbose', help="verbose remote", action='store_true')
    remote_parser.add_argument('--global', help="Used to specify a global remote", action='store_true', dest='glob')
    return remote_parser

def add_pull_parser(sub_parser):
    """
    Adds a sub-parser for the "pull" sub-command to the parser provided.

    :param sub_parser: the parser to add to
    :type sub_parser: <class 'argparse.ArgumentParser'>
    """

    pull_parser = sub_parser.add_parser('pull', help="Pull file from remote")
    pull_parser.add_argument('remote', help="remote to pull")
    pull_parser.add_argument('-k', '--key', help="key of file to pull (from .surround/config.yaml)")

def add_push_parser(sub_parser):
    """
    Adds a sub-parser for the "push" sub-command to the parser provided.

    :param sub_parser: the parser to add to
    :type sub_parser: <class 'argparse.ArgumentParser'>
    """

    push_parser = sub_parser.add_parser('push', help="Push file to remote")
    push_parser.add_argument('remote', help="remote to push")
    push_parser.add_argument('-k', '--key', help="key of file to push (from .surround/config.yaml)")

def add_list_parser(sub_parser):
    """
    Adds a sub-parser for the "list" sub-command to the parser provided.

    :param sub_parser: the parser to add to
    :type sub_parser: <class 'argparse.ArgumentParser'>
    """

    list_parser = sub_parser.add_parser('list', help="List file in remote")
    list_parser.add_argument('remote', help="remote to list")

def write_remote_config(parsed_args, remote_parser, file_to_write):
    """
    Writes the new remote's configuration to the specified YAML file.

    :param parsed_args: arguments parsed from the user (containing the remote name and URL)
    :type parsed_args: <class 'argparse.Namespace'>
    :param remote_parser: the parser for the "remote" sub-command
    :type remote_parser: <class 'argparse.ArgumentParser'>
    :param file_to_write: path to the YAML file
    :type file_to_write: string
    """

    remote_name = parsed_args.name
    remote_url = parsed_args.url

    if remote_name and remote_url:
        BASE_REMOTE.write_config("remote", file_to_write, remote_name, remote_url)
    else:
        print("error: supply remote name and url")
        remote_parser.print_usage()
        print("error: [-a ADD] [-n NAME] [-u URL] are mutually inclusive")

def add_remote(remote_parser, parsed_args):
    """
    Adds a new remote to the current Surround project.
    Writes the new remote's information to the project's ".surround/config.yaml" file.

    :param remote_parser: the parser for the "remote" sub-command
    :type remote_parser: <class 'argparse.ArgumentParser'>
    :param parsed_args: arguments parsed from the user
    :type parsed_args: <class 'argparse.Namespace'>
    """

    verbose = parsed_args.verbose
    global_ = parsed_args.glob

    if verbose:
        print("error: unknown switch [-v VERBOSE]")
        remote_parser.print_usage()
        print("[-a ADD] and [-v VERBOSE] are mutually exclusive")
    else:
        if global_:
            # Make directory if not exists
            home = str(Path.home())
            os.makedirs(os.path.dirname(os.path.join(home, ".surround/config.yaml")), exist_ok=True)
            write_remote_config(parsed_args, remote_parser, os.path.join(home, ".surround/config.yaml"))
        else:
            if is_surround_project():
                actual_current_dir = os.getcwd()
                os.chdir(get_project_root_from_current_dir())
                write_remote_config(parsed_args, remote_parser, ".surround/config.yaml")
                os.makedirs(parsed_args.name, exist_ok=True)
                os.chdir(actual_current_dir)
            else:
                print("error: not a surround project")

def print_remote_info(parsed_args, remotes):
    """
    Prints the collection of remotes to the console.
    If the "--verbose" argument is provided then the URL will be displayed too.

    :param parsed_args: arguments parsed from the user (may contain verbose arg)
    :type parsed_args: <class 'argparse.Namespace'>
    :param remotes: collection of remotes
    :type remotes: dictionary (key = remote name, value = URL)
    """

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

def parse_store_args(remote_parser, parsed_args, extra_args):
    """
    Executes the main "store" command, which in-turn executes one of the sub-commands
    or shows help if no sub-command is specified.

    :param remote_parser: the parser
    :type remote_parser: <class 'argparse.ArgumentParser'>
    :param parsed_args: the arguments parsed from user input
    :type parsed_args: <class 'argparse.Namespace'>
    """

    if parsed_args.sub_command == "remote":
        parse_remote_args(remote_parser, parsed_args)
    elif parsed_args.sub_command == "pull":
        parse_pull_args(parsed_args)
    elif parsed_args.sub_command == "push":
        parse_push_args(remote_parser, parsed_args, extra_args)
    elif parsed_args.sub_command == "list":
        parse_list_args(remote_parser, parsed_args, extra_args)
    else:
        remote_parser.print_help()

def parse_remote_args(remote_parser, parsed_args):
    """
    Executes the "remote" sub-command which will either add new remote
    or list remotes in the current project depending on the arguments.

    :param remote_parser: argument parser used for the "remote" sub-command
    :type remote_parser: <class 'argparse.ArgumentParser'>
    :param parsed_args: the arguments parsed from the user
    :type parsed_args: <class 'argparse.Namespace'>
    """

    global_ = parsed_args.glob
    add = parsed_args.add
    remote_name = parsed_args.name
    remote_url = parsed_args.url

    if add:
        add_remote(remote_parser, parsed_args)
    elif remote_name or remote_url:
        print("error: unknown switch [-n NAME] [-u URL]")
    else:
        if global_:
            remotes = BASE_REMOTE.read_all_from_global_config("remote")
            print_remote_info(parsed_args, remotes)
        else:
            if is_surround_project():
                actual_current_dir = os.getcwd()
                os.chdir(get_project_root_from_current_dir())
                remotes = BASE_REMOTE.read_all_from_local_config("remote")
                print_remote_info(parsed_args, remotes)
                os.chdir(actual_current_dir)
            else:
                print("error: not a surround project")

def parse_pull_args(parsed_args):
    """
    Executes the "pull" sub-command which pulls a file from a specified remote.

    :param parsed_args: arguments parsed from the user (will contain the file name and remote name)
    :type parsed_args: <class 'argparse.Namespace'>
    """

    if is_surround_project():
        actual_current_dir = os.getcwd()
        os.chdir(get_project_root_from_current_dir())
        path_to_remote = BASE_REMOTE.get_path_to_remote(parsed_args.remote)
        if path_to_remote is None:
            print(BASE_REMOTE.message)
            return

        current_remote = get_corresponding_remote(path_to_remote)
        key = parsed_args.key
        if key:
            message = current_remote.pull(parsed_args.remote, key)
            print(message)
        else:
            messages = current_remote.pull(parsed_args.remote, key)
            for message in messages:
                print(message)
        os.chdir(actual_current_dir)
    else:
        print("error: not a surround project")

def parse_push_args(parser, parsed_args, extra_args):
    """
    Executes the "push" sub-command which pushes a file to a specified remote.

    :param parsed_args: arguments parsed from the user (will contain the file name and remote name)
    :type parsed_args: <class 'argparse.Namespace'>
    """

    if is_surround_project():
        actual_current_dir = os.getcwd()
        os.chdir(get_project_root_from_current_dir())
        path_to_remote = BASE_REMOTE.get_path_to_remote(parsed_args.remote)
        if path_to_remote is None:
            print(BASE_REMOTE.message)
            return

        current_remote = get_corresponding_remote(path_to_remote)
        key = parsed_args.key
        if key:
            message = current_remote.push(parsed_args.remote, key)
            print(message)
        else:
            messages = current_remote.push(parsed_args.remote, key)
            for message in messages:
                print(message)
        os.chdir(actual_current_dir)
    else:
        print("error: not a surround project")

def parse_list_args(parser, parsed_args, extra_args):
    """
    Executes the "list" sub-command which lists all the files in a specified remote.

    :param parsed_args: arguments parsed from the user (will contain the remote name)
    :type parsed_args: <class 'argparse.Namespace'>
    """

    if is_surround_project():
        actual_current_dir = os.getcwd()
        os.chdir(get_project_root_from_current_dir())
        path_to_remote = BASE_REMOTE.get_path_to_remote(parsed_args.remote)
        if path_to_remote is None:
            print(BASE_REMOTE.message)
            return

        current_remote = get_corresponding_remote(path_to_remote)
        response = current_remote.list_(parsed_args.remote)
        if isinstance(response, list):
            for remote_file in response:
                print(remote_file)
        else:
            print(response)
        os.chdir(actual_current_dir)
    else:
        print("error: not a surround project")

def get_corresponding_remote(remote):
    """
    Returns the remote corresponding to the URL given.
    NOTE: Only returns an instance of a Local remote, will be fully implemented later.

    :param remote: URL for the remote
    :type remote: string
    :return: the remote object that corresponds to the URL
    :rtype: <class 'surround.remote.base.BaseRemote'>
    """

    return LOCAL
