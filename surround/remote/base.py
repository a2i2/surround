import os
from abc import ABC, abstractmethod

'''
    Interface for remote
'''

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class BaseRemote(ABC):
    def write_remote_to_file(self, file_, name, path):
        '''Write remote to a file

        @param {str} file_: file to write
        @param {str} name: name of the remote
        @param {str} path: path to the remote
        '''
        # Make directory if not exists
        os.makedirs(os.path.dirname(file_), exist_ok=True)

        file_ = open(file_, "a")
        file_.write("\n")
        file_.write(name + ": " + path)
        file_.close()

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
