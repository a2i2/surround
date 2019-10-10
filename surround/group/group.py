import os
import shutil
import math
from pathlib import Path

def group_directory(directory, file_extension, group_size):
    """
    Group large amount of files into indexed subfolders containing the specified amount
    of files.

    :param directory: path to the directory to group
    :type directory: str
    :param file_extension: extension of the files to group
    :type file_extension: str
    :param group_size: size of the subfolders
    :type group_size: int
    :return: number of sub-folders created
    :rtype: int
    """

    if not file_extension.startswith("."):
        file_extension = "." + file_extension

    # Get all files in directory
    files = list(Path(directory).glob("**/*%s" % file_extension))
    num_folders = math.ceil(len(files) / float(group_size))

    # Move all files into indexed groups
    for i in range(num_folders):
        os.mkdir(os.path.join(directory, "%i" % i))
        for _ in range(group_size):
            if files:
                filepath = files.pop()
                shutil.move(filepath, os.path.join(directory, "%i" % i, os.path.basename(filepath)))
            else:
                break

    return num_folders

def undo_group_directory(directory, file_extension):
    """
    Undo grouping of a directory, restoring the directory back to the original structure.
    Removing all the subfolders.

    :param directory: path to the directory to un-group
    :type directory: str
    :param file_extension: extension of the files to process
    :type file_extension: str
    :param perform_move: move the files from the subfolders into the root
    :type perform_move: bool
    :return: the number of files put back to normal
    :rtype: int
    """

    # Move all files back to directory
    if not file_extension.startswith("."):
        file_extension = "." + file_extension

    # Get all files in directory (even sub-directories)
    files = list(Path(directory).glob("**/*%s" % file_extension))

    # Move all files back
    for filepath in files:
        shutil.move(filepath, os.path.join(directory, os.path.basename(filepath)))

    # Remove all the indexed directories
    counter = 0
    while True:
        current_dir = os.path.join(directory, str(counter))
        if os.path.isdir(current_dir):
            os.rmdir(current_dir)
            counter += 1
        else:
            break

    return len(files)
