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

    def read_data_from_surround_local_config(self, file_):
        """Get the associated data file

        :param file_: associated data file
        :type file_: str
        """

        config = Config()

        # Get file
        config.read_config_files([".surround/config.yaml"])
        return config["data"][file_]

    def read_remote_from_surround_global_config(self, remote):
        """Get global remote

        :param remote: remote to find
        :type remote: str
        """

        config = Config()

        home = str(Path.home())

        if Path(home + "/.surround/config.yaml").exists():
            config.read_config_files([home + "/.surround/config.yaml"])
            remotes = config.get("remote", None)
            if remotes:
                remote_to_get = remotes.get(remote, None)
                return remote_to_get
            else:
                return None
        else:
            print("No global config, try setting up a global remote first")

    def read_remote_from_surround_local_config(self, remote):
        """Get local remote

        :param remote: remote to find
        :type remote: str
        """

        config = Config()

        if Path(".surround/config.yaml").exists():
            config.read_config_files([".surround/config.yaml"])
            remotes = config.get("remote", None)
            if remotes:
                remote_to_get = remotes.get(remote, None)
                return remote_to_get
            else:
                return None
        else:
            print("No local remote, searching in global remotes")

    def read_remote_from_surround_config(self, remote):
        local_remote = self.read_remote_from_surround_local_config(remote)
        global_remote = self.read_remote_from_surround_global_config(remote)
        if local_remote:
            return local_remote
        elif global_remote:
            return global_remote
        else:
            print("No remote named " + remote)

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
