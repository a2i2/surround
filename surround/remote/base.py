import os
from abc import abstractmethod
from pathlib import Path
from surround.config import Config

'''
    Interface for remote
'''

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class BaseRemote(object):

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

    def read_from_config(self, what_to_read, key):
        local = self.read_from_local_config(what_to_read, key)
        
        if local:
            return local
        else:
            print("Not found in local, searching in global config")
            return self.read_from_global_config(what_to_read, key)

    def read_from_local_config(self, what_to_read, key):
        config = Config()

        if Path(".surround/config.yaml").exists():
            config.read_config_files([".surround/config.yaml"])
            read_items = config.get(what_to_read, None)
            if read_items:
                return read_items.get(key, None)
            else:
                return None
        else:
            print("No local config")
            return None

    def read_from_global_config(self, what_to_read, key):
        config = Config()
        home = str(Path.home())

        if Path(home + "/.surround/config.yaml").exists():
            config.read_config_files([home + "/.surround/config.yaml"])
            read_items = config.get(what_to_read, None)
            if read_items:
                return read_items.get(key, None)
            else:
                return None
        else:
            print("No global config")

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
