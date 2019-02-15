import os
from shutil import copyfile

from .config import Config

'''
Handles file I/O
'''

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/14'

'''
    Write remote to file

    @param {str} filename: file to write
    @param {str} name: name of the remote
    @param {str} path: path to the remote
'''
def write_remote_to_file(filename, name, path):
    file_ = open(filename, "a")
    file_.write("\n")
    file_.write(name + " = " + path)
    file_.close()


def pull_data(file_):
    """Pull data from remote

        :param file_: Path to yaml file that contains information about file to pull
        :type file_: str
    """
    config = Config()

    # Get file to pull
    config.read_config_files([file_])
    remote_dir_name = config['dir-name']
    file_to_pull = os.path.splitext(os.path.basename(file_))[0]

    # Read remotes
    config.read_config_files([".surround/config.yaml"])

    copyfile(config['data'] + "/" + remote_dir_name + "/" + file_to_pull, os.path.splitext(file_)[0])
