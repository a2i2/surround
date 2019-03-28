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

    def add(self, add_to, key):
        """Add data to remote

        :param add_to: remote to add to
        :type add_to: str
        :param key: file to add
        :type key: str
        """
        project_name = self.get_project_name()
        if project_name is None:
            return self.message

        path_to_local_file = Path(os.path.join(add_to, key))
        path_to_remote = self.read_from_config("remote", add_to)
        if path_to_remote:
            # Append filename
            path_to_remote_file = os.path.join(path_to_remote, project_name, key)
            if Path(path_to_local_file).is_file() or Path(path_to_remote_file).is_file():
                self.write_config(add_to, ".surround/config.yaml", key)
                self.add_message("info: file added successfully", False)
            else:
                self.add_message("error: " + key + " not found.", False)
        else:
            self.add_message("error: no remote named " + add_to, False)
        return self.message

    def pull(self, what_to_pull, key=None):
        """Pull from remote

        :param what_to_pull: what to pull from remote. By convention it is remote name. If remote name is data, it will pull data.
        :type what_to_pull: str
        :param key: file to pull
        :type key: str
        """
        project_name = self.get_project_name()
        if project_name is None:
            return self.messages

        if key:
            path_to_remote = self.read_from_config("remote", what_to_pull)
            relative_path_to_remote_file = os.path.join(project_name, key)
            path_to_local_file = os.path.join(what_to_pull, key)

            if self.file_exists_locally(path_to_local_file):
                return self.message

            os.makedirs(what_to_pull, exist_ok=True)
            if self.file_exists_on_remote(path_to_remote, relative_path_to_remote_file, False):
                response = self.pull_file(what_to_pull, key, path_to_remote, relative_path_to_remote_file, path_to_local_file)
                self.add_message(response)
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
    def pull_file(self, what_to_pull, key, path_to_remote, relative_path_to_remote_file, path_to_local_file):
        """Get the file stored on the remote

        :param what_to_pull: what to pull from remote
        :type what_to_pull: str
        :param path_to_remote: path to the remote.
        :type path_to_remote: str
        :param relative_path_to_remote_file: path to file on remote relative to the remote path
        :type relative_path_to_remote_file: str
        :param path_to_local_file: path to the local file
        :type path_to_local_file: str
        """

    def push(self, what_to_push, key=None):
        """Push to remote

        :param what_to_push: what to push to remote. By convention it is remote name. If remote name is data, it will push data.
        :type what_to_push: str
        :param key: file to push
        :type key: str
        """
        project_name = self.get_project_name()
        if project_name is None:
            return self.messages

        if key:
            path_to_remote = self.read_from_config("remote", what_to_push)
            path_to_remote_file = os.path.join(path_to_remote, project_name, key)
            relative_path_to_remote_file = os.path.join(project_name, key)

            if self.file_exists_on_remote(path_to_remote, relative_path_to_remote_file):
                return self.message

            path_to_local_file = os.path.join(what_to_push, key)
            os.makedirs(os.path.dirname(path_to_remote_file), exist_ok=True)
            if path_to_remote_file and self.file_exists_locally(path_to_local_file, False):
                response = self.push_file(what_to_push, key, path_to_remote, relative_path_to_remote_file, path_to_local_file)
                self.add_message(response)
            else:
                self.add_message("error: file does not exist")
            return self.message

        files_to_push = self.read_all_from_local_config(what_to_push)
        self.messages = []
        if files_to_push:
            for file_to_push in files_to_push:
                self.push(what_to_push, file_to_push)
        else:
            self.add_message("error: No file added to " + what_to_push)
        return self.messages

    @abstractmethod
    def push_file(self, what_to_push, key, path_to_remote, relative_path_to_remote_file, path_to_local_file):
        """Get the file stored on the remote

        :param what_to_push: what to push to remote
        :type what_to_push: str
        :param path_to_remote: path to the remote.
        :type path_to_remote: str
        :param relative_path_to_remote_file: path to file on remote relative to the remote path
        :type relative_path_to_remote_file: str
        :param path_to_local_file: path to the local file
        :type path_to_local_file: str
        """

    def list_(self, remote_to_list):
        """General method for listing files on the remote

        :param remote_to_list: remote to list
        :type remote_to_list: str
        """
        project_name = self.get_project_name()
        if project_name is None:
            return self.message

        path_to_remote = self.read_from_config("remote", remote_to_list)
        if path_to_remote:
            return self.list_files(path_to_remote, project_name)
        return "error: no remote named " + remote_to_list

    @abstractmethod
    def list_files(self, path_to_remote, project_name):
        """List the files in the remote

        :param path_to_remote: path to the remote
        :type path_to_remote: str
        :param project_name: name of the project
        :type project_name: str
        """
        raise NotImplementedError

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
    def file_exists_on_remote(self, path_to_remote, relative_path_to_remote_file, append_to=True):
        """Check if file is already present on remote. This is used to prevent overwriting of files.

        :param path_to_remote: path to remote
        :type path_to_remote: str
        :param relative_path_to_remote_file: path to file on remote relative to the remote path
        :type relative_path_to_remote_file: str
        :param append_to: Append message to messages list. By default, it is true.
        :type append_to: bool
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
