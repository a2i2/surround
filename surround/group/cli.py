import os
import argparse

from .group import group_directory, undo_group_directory

def is_valid_dir(arg_parser, arg):
    """
    A simple function to validate a directory

    :param arg_parser: the parser
    :type arg_parser: :class:`argparse.ArgumentParser`
    :param arg: the directory we're checking
    :type arg: str
    """

    if not os.path.isdir(arg):
        arg_parser.error("Invalid directory %s" % arg)
        return arg

    return arg

def is_valid_reset_dir(directory):
    """
    A simple function to validate a reset directory

    :param directory: the path we're checking
    :type directory: str
    :return: True if the directory is valid for reset
    :rtype: bool
    """

    if not os.path.isdir(directory):
        print("Invalid directory %s" % directory)
        return False

    if not os.path.isdir(os.path.join(directory, "0")):
        print("Unable to reset this directory, doesn't seem a group was applied here")
        return False

    return True

def get_group_parser():
    """
    Returns the parser used for the group tool which defines all the available arguments.
    This can be used for generating documentation about the tool using Sphinx.

    :return: the parser object
    :rtype: :class:`argparse.ArgumentParser`
    """

    parser = argparse.ArgumentParser(description='Randomly assign data to test, training, and validate sets')
    parser.add_argument("directory", help="Path to directory of files that will be grouped", type=lambda x: is_valid_dir(parser, x))
    parser.add_argument("-r", "--reset", help="Reset the directory given", action="store_true")
    parser.add_argument("-s", "--size", type=int, help="How much files to put in each group (default: 100)", default=100)

    return parser

def execute_group_tool(parser, args, extra_args):
    """
    Execute the group command-line tool using arguments parsed from the user.

    :param parser: the parser of the group tool
    :type parser: :class:`argparse.ArgumentParser`
    :param args: the arguments parsed from the user
    :type args: :class:`argparse.Namespace`
    """

    # Check the directory can be reset (if reset requested)
    if args.reset and not is_valid_reset_dir(args.directory):
        return

    if not args.reset:
        num_sub_folders = group_directory(args.directory, "*", args.size)
        print("Sub-folders created: %i" % num_sub_folders)
    else:
        num_files = undo_group_directory(args.directory, "*")
        print("Number of files reset: %i" % num_files)

def main():
    """
    Entry point when this script is ran locally.
    Parses the arguments from the user's input and executes the group tool.
    """

    parser = get_group_parser()
    args = parser.parse_args()

    execute_group_tool(parser, args, [])

if __name__ == "__main__":
    main()
