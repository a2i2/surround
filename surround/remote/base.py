import os
import yaml
from abc import abstractmethod
from pathlib import Path
from surround.config import Config

'''
    Interface for remote
'''

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class BaseRemote(object):

    def write_config(self, what_to_write, file_, name, path):
        """Write config to a file

        :param what_to_write: For example remote, data, model etc.
        :type what_to_write: str
        :param file_: file to write
        :type file_: str
        :param name: name of the remote
        :type name: str
        :param path: path to the remote
        :type path: str
        """

        # Make directory if not exists
        os.makedirs(os.path.dirname(file_), exist_ok=True)

        if os.path.exists(file_):
            with open(file_, "r") as f:
                read_config = yaml.load(f) or {}
        else:
            read_config = {}

        if what_to_write in read_config:
            read_config[what_to_write][name] = path
        else:
            read_config[what_to_write] = {
                name: path
            }

        with open(file_, "w") as f:
            yaml.dump(read_config, f, default_flow_style=False)

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
