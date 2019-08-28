"""
A script to randomly move files in a directory to a test, train and
validate folder.

This script is intended to be used on projects where the data is made
up of multiple files e.g. images or email files.
"""

import sys
import os
import argparse

from .split_data import split_directory, undo_split_directory, split_file, undo_split_file

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

def is_valid_file(arg_parser, arg):
    """
    A simple function to validate a file path

    :param arg_parser: the parser
    :type arg_parser: :class:`argparse.ArgumentParser`
    :param arg: the file path we're checking
    :type arg: str
    """

    if not os.path.isfile(arg):
        arg_parser.error("Invalid file path %s" % arg)
        return arg

    return arg

def get_split_parser():
    """
    Returns the parser used for the split tool which defines all the available arguments.
    This can be used for generating documentation about the tool using Sphinx.

    :return: the parser object
    :rtype: :class:`argparse.ArgumentParser`
    """

    parser = argparse.ArgumentParser(description='Randomly assign data to test, training, and validate sets')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--text-file", help="Split text file into train/test/validate sets", type=lambda x: is_valid_file(parser, x))
    group.add_argument("-d", "--directory", help="Split directory into train/test/validate sets", type=lambda x: is_valid_dir(parser, x))
    group.add_argument("-r", "--reset", help="Path to directory containing train/test/validate folders to reset", type=lambda x: is_valid_dir(parser, x))

    parser.add_argument("-e", "--extension", help="File extension of the files to process (default: *)", type=str, default="*")
    parser.add_argument("-tr", "--train", type=int, help="Percentage of files for training (default: 80%)", default=80)
    parser.add_argument("-te", "--test", type=int, help="Percentage of files for test (default: 10%)", default=10)
    parser.add_argument("-va", "--validate", type=int, help="Percentage of files for validate (default: 10%)", default=10)
    parser.add_argument("-nv", "--no-validate", action="store_true", help="Don't produce a validation set when splitting")
    parser.add_argument("-ns", "--no-shuffle", action="store_true", help="Don't randomise when splitting data")
    parser.add_argument("-nh", '--no-header', action="store_true", help="Use this flag when the text file has no headers")

    return parser

def validate_args(args):
    """
    Validates the arguments given to the split tool.

    :param args: the arguments
    :type args: :class:`argparse.Namespace`
    """

    # If default values, adjust so proportions add up to 100
    if args.no_validate and args.train == 80 and args.test == 10:
        args.test = 20

    if args.no_validate and args.train + args.test != 100:
        print("Test and train proportions should add up to 100.")
        return False

    if not args.no_validate and args.train + args.test + args.validate != 100:
        print("Test, train and validate proportions should add up to 100.")
        return False

    # Ensure reset folder given is valid (contains expected directories)
    if args.reset:
        dirs = [path for path in os.listdir(args.reset) if os.path.isdir(os.path.join(args.reset, path))]
        expected = ['train', 'test']

        if not all([exp in dirs for exp in expected]):
            print("Cannot reset this folder since there are no test/train/validate folders!")
            return False

    return True

def reset_directory(args):
    """
    Reset a directory that has been split using the split tool.

    :param args: the arguments parsed from the user
    :type args: :class:`argparse.Namespace`
    """

    # Try and guess the extension
    if not args.extension:
        files = os.listdir(os.path.join(args.reset, "test"))
        _, args.extension = os.path.splitext(files[0])

        if args.extension:
            args.extension = args.extension[1:]
        else:
            print("Failed to guess which extension was used during the initial split")
            return

    # Reset the split directory operation
    undo_split_directory(args.reset, args.extension)

def reset_file(reset_path, no_header):
    """
    Reset a text file that has been split using the split tool

    :param reset_path: the directory the result of the split is in
    :type reset_path: str
    """

    test_path = os.path.join(reset_path, "test")
    files = os.listdir(test_path)
    files = [x for x in files if os.path.isfile(os.path.join(test_path, x))]

    if files:
        file_name = os.path.basename(files[0])
        undo_split_file(os.path.join(reset_path, file_name), no_header)
    else:
        print("Failed to reset, invalid directory!")

def is_directory_split_file(directory):
    """
    Returns whether the directory provided contains files generated from a split file operation

    :param directory: the path to where the split occured
    :type directory: str
    :return: whether the directory is the result of a split file operation
    :rtype: bool
    """

    expected = ['train', 'test']
    dirs = os.listdir(directory)

    # Must contain at least train and validate folders
    if not all([exp in dirs for exp in expected[:2]]):
        return False

    test_files = os.listdir(os.path.join(directory, 'test'))
    train_files = os.listdir(os.path.join(directory, 'train'))

    unique_values = set(test_files + train_files)

    # The directory is from a split file if there is one file name across both train and test sets
    return len(unique_values) == 1

def execute_split_tool(parser, args):
    """
    Execute the split command-line tool using arguments parsed from the user.

    :param parser: the parser of the split tool
    :type parser: :class:`argparse.ArgumentParser`
    :param args: the arguments parsed from the user
    :type args: :class:`argparse.Namespace`
    """

    if not validate_args(args):
        sys.exit(1)

    if args.directory and args.extension:
        split_directory(args.directory, args.extension, args.train, args.test, args.validate, args.no_validate, args.no_shuffle)
    elif args.reset:
        if is_directory_split_file(args.reset):
            reset_file(args.reset, args.no_header)
        else:
            reset_directory(args)
    elif args.text_file:
        split_file(args.text_file, args.train, args.test, args.validate, args.no_validate, args.no_shuffle, args.no_header)
    else:
        print("Invalid arguments, use --help for more information")

def main():
    """
    Entry point when this script is ran locally.
    Parses the arguments from the user's input and executes the split tool.
    """

    parser = get_split_parser()
    args = parser.parse_args()

    execute_split_tool(parser, args)

if __name__ == "__main__":
    main()
