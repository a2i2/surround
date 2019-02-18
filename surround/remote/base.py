import os
from abc import ABC, abstractmethod

'''
    Interface for remote
'''

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class BaseRemote(ABC):
    def write_remote_to_file(self, file_, name, path):
        """Write remote to a file

        :param file_: file to write
        :type file_: str
        :param name: name of the remote
        :type name: str
        :param path: path to the remote
        :type path: str
        """
        # Make directory if not exists
        os.makedirs(os.path.dirname(file_), exist_ok=True)

        with open(file_, "a") as f:
            f.write(name + ": " + path + "\n")

    @abstractmethod
    def add(self, file_):
        """Add data to remote

        :param file_: file to add
        :type file_: str
        """

    @abstractmethod
    def pull(self, file_=None):
        """Pull data from remote

        :param file_: file to pull
        :type file_: str
        """

    @abstractmethod
    def push(self, file_=None):
        """Push data to remote

        :param file_: file to push
        :type file_: str
        """

    def get_file_name(self, file_):
        """Extract filename from path

        :param file_: path to file
        :type file_: str
        """
        return os.path.basename(file_)
