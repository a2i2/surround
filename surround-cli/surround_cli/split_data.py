"""A script to randomly move files in a directory to a test, train and
validate folder.

This script is intended to be used on projects where the data is made
up of multiple files e.g. images or email files.

Usage: python3 split_data.py <directory> <file extension>

TODO: Add a flag to sort data into sub-folders based on a prefix for file names
TODO: Make sure reset works for all flags
TODO: Modify script to work on a CSV file. In this case split the CSV file into multiple files under each folder.

"""

import sys
import os
from pathlib import Path
import argparse
import random
import shutil

def is_valid_dir(arg_parser, arg):
    """A simple function to validate a directory"""
    if not os.path.isdir(arg):
        arg_parser.error("Invalid directory %s" % arg)
        return arg
    return arg

def prepare_folder(directory, file_extension):
    if not os.path.isdir(directory):
        print("%s is not a valid directory" % directory)
        return

    if not file_extension.startswith("."):
        file_extension = "." + file_extension

    test_dir = os.path.join(directory, "test")
    train_dir = os.path.join(directory, "train")
    validate_dir = os.path.join(directory, "validate")

    files = list(Path(directory).glob("**/*%s" % file_extension))

    return files, test_dir, train_dir, validate_dir


def main(directory, file_extension, train, test, validate):
    """Main function for randomly assigning files in a directory to test,
        train and validate folders.

    """
    files, test_dir, train_dir, validate_dir = prepare_folder(directory, file_extension)
    os.makedirs(test_dir)
    os.makedirs(train_dir)
    os.makedirs(validate_dir)

    train_count = int(len(files) * train / 100)
    test_count = int(len(files) * test / 100)

    # Account for rounding errors
    validate_count = len(files) - train_count - test_count

    random.shuffle(files)

    def process_files(count, folder):
        for _ in range(0, count):
            file_path = files.pop()
            shutil.move(file_path, os.path.join(folder, os.path.basename(file_path)))

    process_files(train_count, train_dir)
    process_files(test_count, test_dir)
    process_files(validate_count, validate_dir)

    print("Train count: %d" % train_count)
    print("Test count: %d" % test_count)
    print("Validate count: %d" % validate_count)


def undo(directory, file_extension):
    if not os.path.isdir(os.path.join(directory, "test")) or not os.path.isdir(os.path.join(directory, "train")) or not os.path.isdir(os.path.join(directory, "validate")):
        print("test, train or validate folders missing from %s" % directory)
        return

    files, test_dir, train_dir, validate_dir = prepare_folder(directory, file_extension)

    for a_file in files:
        shutil.move(a_file, os.path.join(directory, os.path.basename(a_file)))

    os.removedirs(test_dir)
    os.removedirs(train_dir)
    os.removedirs(validate_dir)

    print("File count %d" % len(files))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=
        'Randomly assign files in a directory to test, train and validate folders.'
    )

    parser.add_argument(
        "directory",
        help="Directory with files to process",
        type=lambda x: is_valid_dir(parser, x))
    parser.add_argument(
        "file_extension", help="File extension for files to process", type=str)


    parser.add_argument("-r", "--reset", action='store_true', help="Reset the directory structure")
    parser.add_argument("-tr", "--train", type=int, help="Percentage of files for training", default=80)
    parser.add_argument("-te", "--test", type=int, help="Percentage of files for training", default=10)
    parser.add_argument("-va", "--validate", type=int, help="Percentage of files for training", default=10)

    args = parser.parse_args()

    if args.train + args.test + args.validate != 100:
        print("Test, train and validate proportions should add up to 100.")
        sys.exit(1)

    try:
        if args.reset:
            undo(args.directory, args.file_extension)
        else:
            main(args.directory, args.file_extension, args.train, args.test, args.validate)
    except FileExistsError:
        print("test, train or validate already exist in %s" % args.directory)
