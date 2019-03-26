import os
from abc import abstractmethod
from pathlib import Path
import yaml
from surround.config import Config

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class BaseRemote():

    def __init__(self):
        self.message = ""
        self.messages = []

    def write_config(self, what_to_write, file_, name, path=None):
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

        if os.path.exists(file_):
            with open(file_, "r") as f:
                read_config = yaml.safe_load(f) or {}
        else:
            read_config = {}

        if path is None:
            if what_to_write in read_config and name not in read_config[what_to_write]:
                read_config[what_to_write].append(name)
            else:
                read_config[what_to_write] = [name]
        else:
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
        return local if local is not None else self.read_from_global_config(what_to_read, key)

    def read_from_local_config(self, what_to_read, key):
        config = Config()

        if Path(".surround/config.yaml").exists():
            config.read_config_files([".surround/config.yaml"])
            read_items = config.get(what_to_read, None)
            return read_items.get(key, None) if read_items is not None else None

    def read_from_global_config(self, what_to_read, key):
        config = Config()
        home = str(Path.home())
        if Path(os.path.join(home, ".surround/config.yaml")).exists():
            config.read_config_files([os.path.join(home, ".surround/config.yaml")])
            read_items = config.get(what_to_read, None)
            return read_items.get(key, None) if read_items is not None else None

    def read_all_from_local_config(self, what_to_read):
        config = Config()

        if Path(".surround/config.yaml").exists():
            config.read_config_files([".surround/config.yaml"])
            read_items = config.get(what_to_read, None)
            return read_items

    def read_all_from_global_config(self, what_to_read):
        config = Config()
        home = str(Path.home())

        if Path(os.path.join(home, ".surround/config.yaml")).exists():
            config.read_config_files([os.path.join(home, ".surround/config.yaml")])
            read_items = config.get(what_to_read, None)
            return read_items

    @abstractmethod
    def add(self, add_to, key):
        """Add data to remote

        :param file_: file to add
        :type key: str
        """

    def pull(self, what_to_pull, key=None):
        """Pull data from remote

        :param file_: file to pull
        :type key: str
        """
        project_name = self.get_project_name()
        if project_name is None:
            return self.messages

        if key:
            path_to_remote = self.read_from_config("remote", what_to_pull)
            file_to_pull = os.path.join(path_to_remote, project_name, key)
            path_to_pulled_file = os.path.join(what_to_pull, key)

            if self.file_exists_locally(path_to_pulled_file):
                return self.message

            os.makedirs(what_to_pull, exist_ok=True)
            if self.file_exists_on_remote(file_to_pull, False):
                self.pull_file(what_to_pull, key, file_to_pull, path_to_pulled_file)
                self.add_message("info: " + key + " pulled successfully")
            else:
                self.add_message("error: file does not exist")
            return self.message

        files_to_pull = self.read_all_from_local_config(what_to_pull)
        self.messages = []
        if files_to_pull:
            for file_to_pull in files_to_pull:
                self.pull(what_to_pull, file_to_pull)
        else:
            self.add_message("error: No file added to " + what_to_pull)
        return self.messages

    @abstractmethod
    def pull_file(self, what_to_pull, key, file_to_pull, path_to_pulled_file):
        """Get the file stored on the remote

        :param path_to_pulled_file: path where do you want to store file
        :type path_to_pulled_file: str
        """

    @abstractmethod
    def push(self, what_to_push, key=None):
        """Push data to remote

        :param file_: file to push
        :type key: str
        """

    def get_file_name(self, file_):
        """Extract filename from path

        :param file_: path to file
        :type file_: str
        """
        return os.path.basename(file_)

    def get_project_name(self):
        project_name = self.read_from_local_config("project-info", "project-name")
        if project_name:
            return project_name
        self.add_message("error: project name not present in config")

    def add_message(self, message, append_to=True):
        """Store message and if required append that to the list

        :param message: message to display
        :type message: str
        :param append_to: append message to messages list
        :type append_to: bool
        """
        self.message = message
        if append_to:
            self.messages.append(self.message)

    @abstractmethod
    def file_exists_on_remote(self, path_to_remote_file, append_to=True):
        """Check if file is already present on remote. This is used to prevent overwriting of files.

        :param path_to_remote_file: path to file
        :type path_to_remote_file: str
        """

    def file_exists_locally(self, path_to_file, append_to=True):
        """Check if file is already present on remote. This is used to prevent overwriting of files.

        :param path_to_file: path to file
        :type path_to_file: str
        :param append_to: Append message to messages list. By default, it is true.
        :type append_to: bool
        """
        if Path(path_to_file).exists():
            self.add_message("info: " + path_to_file + " already exists", append_to)
            return True
