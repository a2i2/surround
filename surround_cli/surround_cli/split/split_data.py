import os
import random
import shutil
from pathlib import Path

# pylint: disable=too-many-locals
def split_file(filepath, train, test, validate, no_validate, no_shuffle, no_header):
    """
    Split CSV dataset into 2-3 separate sets (train/test/validation).
    The original file will be deleted and a folder for each set will be created.

    :param filepath: path to the CSV file
    :type filepath: str
    :param train: percentage of data put into train set
    :type train: int
    :param test: percentage of data put into test set
    :type test: int
    :param validate: percentage of data put into validate set
    :type validate: int
    :param no_validate: if true, don't create validation set
    :type no_validate: bool
    :param no_shuffle: if true, don't shuffle set before splitting
    :type no_shuffle: bool
    :param no_header: if true, don't consider the first line as the header
    :type no_header: bool
    """

    with open(filepath) as f:
        values = f.readlines()

        # Get the header (if any)
        if not no_header:
            header = values[0]
            values = values[1:]

    # Remove the original file
    os.unlink(filepath)

    if not no_shuffle:
        # Shuffle the records
        random.shuffle(values)

    train_count = int(len(values) * train / 100 + 0.5)

    if no_validate:
        test_count = len(values) - train_count
    else:
        test_count = int(len(values) * test / 100 + 0.5)

    # Create paths to train/test/validate sets
    train_path = os.path.join(
        os.path.dirname(os.path.abspath(filepath)), "train", os.path.basename(filepath)
    )
    test_path = os.path.join(
        os.path.dirname(os.path.abspath(filepath)), "test", os.path.basename(filepath)
    )

    if not no_validate:
        validate_count = len(values) - train_count - test_count
        validate_path = os.path.join(
            os.path.dirname(os.path.abspath(filepath)),
            "validate",
            os.path.basename(filepath),
        )
        os.mkdir(os.path.dirname(validate_path))

    # Make their dirs
    os.mkdir(os.path.dirname(train_path))
    os.mkdir(os.path.dirname(test_path))

    def process_data(count, values, path):
        with open(path, "w+") as f:
            if not no_header:
                f.write(header)
            f.writelines(values[:count])
        return values[count:]

    # Export the train/test/validate sets to separate files
    values = process_data(train_count, values, train_path)
    values = process_data(test_count, values, test_path)

    print("Train count: %d" % train_count)
    print("Test count: %d" % test_count)

    if not no_validate:
        values = process_data(validate_count, values, validate_path)
        print("Validate count: %d" % validate_count)


def undo_split_file(filepath, no_header):
    """
    Undo splitting of CSV file.
    This will delete the three sets and put all the data back into the original file.

    :param filepath: path to the original file before splitting
    :type filepath: str
    :param no_header: if true, don't consider the first line as the header
    :type no_header: bool
    """

    # Get the paths to the split data
    name = os.path.basename(filepath)
    train_path = os.path.join(os.path.dirname(os.path.abspath(filepath)), "train", name)
    test_path = os.path.join(os.path.dirname(os.path.abspath(filepath)), "test", name)
    validate_path = os.path.join(
        os.path.dirname(os.path.abspath(filepath)), "validate", name
    )

    with open(train_path) as f:
        train_frame = f.readlines()
        if not no_header:
            header = train_frame[0]
            train_frame = train_frame[1:]

    with open(test_path) as f:
        test_frame = f.readlines()
        if not no_header:
            header = test_frame[0]
            test_frame = test_frame[1:]

    validate_frame = None
    if os.path.isfile(validate_path):
        with open(validate_path) as f:
            validate_frame = f.readlines()
            if not no_header:
                header = validate_frame[0]
                validate_frame = validate_frame[1:]

    # Put all sets back into one frame
    original = train_frame + test_frame

    if validate_frame is not None:
        original.extend(validate_frame)

    # Save original file
    with open(filepath, "w+") as f:
        if not no_header:
            f.write(header)

        f.writelines(original)

    # Remove split data
    os.unlink(train_path)
    os.unlink(test_path)

    if validate_frame is not None:
        os.unlink(validate_path)
        os.removedirs(os.path.dirname(validate_path))

    # Remove the directories
    os.removedirs(os.path.dirname(train_path))
    os.removedirs(os.path.dirname(test_path))

    print("Record count: %d" % len(original))


def prepare_folder(directory, file_extension):
    """
    Generates a files list and train/test/validate paths for the specified directory.

    :param directory: path to directory to prepare
    :type directory: str
    :param file_extension: extension of files that will be processed
    :type file_extension: str
    """

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


# pylint: disable=too-many-locals
def split_directory(
    directory, file_extension, train, test, validate, no_validate, no_shuffle
):
    """
    Splits a directory of files (of a certain extension) into 2-3 separate sets (test/train/validate).

    :param directory: path to directory to split
    :type directory: str
    :param file_extension: extension of files to process
    :type file_extension: str
    :param train: percentage of files assigned to the train set
    :type train: int
    :param test: percentage of files assigned to the test set
    :type test: int
    :param validate: percentage of files assigned to the validate set
    :type validate: int
    :param no_validate: if true, don't create validation set
    :type no_validate: bool
    :param no_shuffle: if true, don't shuffle files before assigning
    :type no_shuffle: bool
    """

    # Create folders and get the files to split
    files, test_dir, train_dir, validate_dir = prepare_folder(directory, file_extension)
    os.makedirs(test_dir)
    os.makedirs(train_dir)

    # Calculate counts from percentages set by the user
    train_count = int(len(files) * train / 100 + 0.5)

    if no_validate:
        test_count = len(files) - train_count
    else:
        test_count = int(len(files) * test / 100 + 0.5)

        os.makedirs(validate_dir)
        validate_count = len(files) - train_count - test_count

    if not no_shuffle:
        # Shuffle files
        random.shuffle(files)

    def process_files(count, folder):
        for _ in range(0, count):
            file_path = files.pop()
            shutil.move(file_path, os.path.join(folder, os.path.basename(file_path)))

    # Split data into train and test sets
    process_files(train_count, train_dir)
    process_files(test_count, test_dir)

    # Split data into validate set (if allowed)
    if not no_validate:
        process_files(validate_count, validate_dir)

    print("Train count: %d" % train_count)
    print("Test count: %d" % test_count)

    if not no_validate:
        print("Validate count: %d" % validate_count)


def undo_split_directory(directory, file_extension):
    """
    Undo splitting of a directory into 2-3 different sets. Restores directory back to
    the original structure.

    :param directory: path to directory to restore
    :type directory: str
    :param file_extension: extension of files to process
    :type file_extension: str
    """

    if not os.path.isdir(os.path.join(directory, "test")) or not os.path.isdir(
        os.path.join(directory, "train")
    ):
        print("test, train or validate folders missing from %s" % directory)
        return

    files, test_dir, train_dir, validate_dir = prepare_folder(directory, file_extension)

    for a_file in files:
        shutil.move(a_file, os.path.join(directory, os.path.basename(a_file)))

    os.removedirs(test_dir)
    os.removedirs(train_dir)

    if os.path.isdir(validate_dir):
        os.removedirs(validate_dir)

    print("File count: %d" % len(files))
