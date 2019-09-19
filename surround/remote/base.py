import os
from abc import abstractmethod
from pathlib import Path
import yaml
from surround.config import Config

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class BaseRemote():
    """
    Abstract base class for all different types of remotes.
    Provides an interface for pushing and pulling data from a remote irrespective of the service used.

    Public methods:
    - add(add_to, key)
    - pull(what_to_pull, key)
    - push(what_to_push, key)
    - list_(remote_name)
    - file_exists_locally(path_to_file, append_to)
    - add_message(message, append_to)
    - get_path_to_remote(remote)
    - get_project_name()
    - get_file_name(file)
    - write_config(what_to_write, file, name, path)
    - read_from_config(what_to_read, key)

    Abstract methods:
    - pull_file(what_to_pull, key, path_to_remote, relative_path_to_remote_file, path_to_local_file)
    - push_file(what_to_push, key, path_to_remote, relative_path_to_remote_file, path_to_local_file)
    - list_files(path_to_remote, project_name)
    - file_exists_on_remote(path_to_remote, relative_path_to_remote_file, append_to)
    """

    def __init__(self):
        self.message = ""
        self.messages = []

    def write_config(self, what_to_write, file_, name, path=None):
        """
        Write configuration data to a YAML file specified.

        :param what_to_write: For example remote, data, model etc.
        :type what_to_write: string
        :param file_: path to configuration file
        :type file_: string
        :param name: name of the remote
        :type name: string
        :param path: path to the remote
        :type path: string
        """

        if os.path.exists(file_):
            with open(file_, "r") as f:
                read_config = yaml.safe_load(f) or {}
        else:
            read_config = {}

        if path is None:
            if what_to_write in read_config and name not in read_config[what_to_write]:
                read_config[what_to_write].append(name)
            elif what_to_write not in read_config:
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
        """
        Reads data from first the local config and if no data found tries the global config.

        :param what_to_read: what data category, for example remote, data, model, etc.
        :type what_to_read: string
        :param key: the key for the data wanted
        :type key: string
        :return: the data found or None if not found
        :rtype: any
        """

        local = self.read_from_local_config(what_to_read, key)
        return local if local is not None else self.read_from_global_config(what_to_read, key)

    def read_from_local_config(self, what_to_read, key):
        """
        Reads data from the local config YAML file.
        The local config file can be found at ".surround/config.yaml".

        :param what_to_read: what data category to read from
        :type what_to_read: string
        :param key: the key for the data wanted
        :type key: string
        :return: the data found or None if not found
        :rtype: any
        """

        config = Config()

        if Path(".surround/config.yaml").exists():
            config.read_config_files([".surround/config.yaml"])
            read_items = config.get(what_to_read, None)
            return read_items.get(key, None) if read_items is not None else None

    def read_from_global_config(self, what_to_read, key):
        """
        Reads data from the global config YAML file.
        The global config file can be found at "$HOME/.surround/config.yaml".

        :param what_to_read: what data category to read from
        :type what_to_read: string
        :param key: the key for the data wanted
        :type key: string
        :return: the data found or None if not found
        :rtype: any
        """

        config = Config()
        home = str(Path.home())
        if Path(os.path.join(home, ".surround/config.yaml")).exists():
            config.read_config_files([os.path.join(home, ".surround/config.yaml")])
            read_items = config.get(what_to_read, None)
            return read_items.get(key, None) if read_items is not None else None

    def read_all_from_local_config(self, what_to_read):
        """
        Reads all data for a specified category from the local config file.
        The local config file can be found at ".surround/config.yaml".

        :param what_to_read: what data category to read all data from
        :type what_to_read: string
        :return: all data contained in the category or None if category not found
        :rtype: any
        """

        config = Config()

        if Path(".surround/config.yaml").exists():
            config.read_config_files([".surround/config.yaml"])
            read_items = config.get(what_to_read, None)
            return read_items

    def read_all_from_global_config(self, what_to_read):
        """
        Reads all data for a specified category from the global config file.
        The global config file can be found at "$HOME/.surround/config.yaml".

        :param what_to_read: what data category to read all data from
        :type what_to_read: string
        :return: all data contained in the category or None if category not found
        :rtype: any
        """

        config = Config()
        home = str(Path.home())

        if Path(os.path.join(home, ".surround/config.yaml")).exists():
            config.read_config_files([os.path.join(home, ".surround/config.yaml")])
            read_items = config.get(what_to_read, None)
            return read_items

    def add(self, add_to, key):
        """
        Add a file to the remote specified.

        :param add_to: remote to add to
        :type add_to: string
        :param key: file to add
        :type key: string
        :return: messages on whether the process completed properly
        :rtype: list of strings
        """

        project_name = self.get_project_name()
        if project_name is None:
            return self.message

        path_to_local_file = Path(os.path.join(add_to, key))
        path_to_remote = self.get_path_to_remote(add_to)
        if path_to_remote is None:
            return self.message

        # Append filename
        path_to_remote_file = os.path.join(path_to_remote, project_name, key)
        if Path(path_to_local_file).is_file() or Path(path_to_remote_file).is_file():
            self.write_config(add_to, ".surround/config.yaml", key)
            self.add_message("info: file added successfully", False)
        else:
            self.add_message("error: " + key + " not found.", False)

        return self.message

    def pull(self, what_to_pull, key=None):
        """
        Pull file(s) from the remote specified, if no file specified, all files will be pulled.
        This will not overwrite already existing files locally.

        :param what_to_pull: what to pull from remote. By convention it is remote name. If remote name is data, it will pull data.
        :type what_to_pull: string
        :param key: file to pull (default: None)
        :type key: string
        :return: messages on whether the process completed successfully
        :rtype: list of strings
        """

        project_name = self.get_project_name()
        if project_name is None:
            return self.messages

        path_to_remote = self.get_path_to_remote(what_to_pull)
        if path_to_remote is None:
            return self.messages

        if key:
            relative_path_to_remote_file = os.path.join(project_name, key)
            path_to_local_file = os.path.join(what_to_pull, key)

            if self.file_exists_locally(path_to_local_file):
                return self.message

            os.makedirs(what_to_pull, exist_ok=True)
            if self.file_exists_on_remote(path_to_remote, relative_path_to_remote_file, False):
                # Ensure the file is being tracked in config
                self.add(what_to_pull, key)

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
        """
        Get the file stored on the remote and save it locally.

        :param what_to_pull: what to pull from remote
        :type what_to_pull: string
        :param path_to_remote: path to the remote
        :type path_to_remote: string
        :param relative_path_to_remote_file: path to file on remote relative to the remote path
        :type relative_path_to_remote_file: string
        :param path_to_local_file: path to the local file
        :type path_to_local_file: string
        :return: message detailing the result of the pulling
        :rtype: string
        """

    def push(self, what_to_push, key=None):
        """
        Push file(s) to the remote, if no file specified then all files will be pushed.

        :param what_to_push: what to push to remote. By convention it is remote name. If remote name is data, it will push data.
        :type what_to_push: string
        :param key: file to push
        :type key: string
        :return: messages detailing the result of the process
        :rtype: list of string or string
        """

        project_name = self.get_project_name()
        if project_name is None:
            return self.messages

        path_to_remote = self.get_path_to_remote(what_to_push)
        if path_to_remote is None:
            return self.messages

        if key:
            path_to_remote_file = os.path.join(path_to_remote, project_name, key)
            relative_path_to_remote_file = os.path.join(project_name, key)

            if self.file_exists_on_remote(path_to_remote, relative_path_to_remote_file):
                return self.message

            path_to_local_file = os.path.join(what_to_push, key)
            os.makedirs(os.path.dirname(path_to_remote_file), exist_ok=True)
            if path_to_remote_file and self.file_exists_locally(path_to_local_file, False):
                # Ensure the file is being tracked in config
                self.add(what_to_push, key)

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
        :type what_to_push: string
        :param path_to_remote: path to the remote.
        :type path_to_remote: string
        :param relative_path_to_remote_file: path to file on remote relative to the remote path
        :type relative_path_to_remote_file: string
        :param path_to_local_file: path to the local file
        :type path_to_local_file: string
        :return: message detailing the result of the process
        :rtype: string
        """

    def list_(self, remote_to_list):
        """
        Returns the list of files contained in the remote specified.

        :param remote_to_list: remote to list
        :type remote_to_list: string
        :return: list of the files or a message on error
        :rtype: list of string or string on error
        """

        project_name = self.get_project_name()
        if project_name is None:
            return self.message

        path_to_remote = self.get_path_to_remote(remote_to_list)
        if path_to_remote is None:
            return self.message

        return self.list_files(path_to_remote, project_name)

    @abstractmethod
    def list_files(self, path_to_remote, project_name):
        """
        Returns a list of files on the remote specified.

        :param path_to_remote: path to the remote
        :type path_to_remote: string
        :param project_name: name of the project
        :type project_name: string
        :return: list of the files or a message on error
        :rtype: list of string or string
        """

        raise NotImplementedError

    def get_file_name(self, file_):
        """
        Extract filename from path specified.

        :param file_: path to file
        :type file_: string
        :return: the filename
        :rtype: string
        """

        return os.path.basename(file_)

    def get_project_name(self):
        """
        Returns the project name found in the local config file.

        :return: the name of the project or None if no project found locally
        :rtype: string
        """

        project_name = self.read_from_local_config("project-info", "project-name")
        if project_name:
            return project_name
        self.add_message("error: project name not present in config")

    def get_path_to_remote(self, remote_to_read):
        """
        Returns the path/URL to the remote saved in configuration.

        :param remote_to_read: the name of the remote
        :type remote_to_read: string
        :return: path/URL of the remote or None if could not be found
        :rtype: string
        """

        remote = self.read_from_config("remote", remote_to_read)
        if remote:
            return remote
        self.add_message("error: no remote named " + remote_to_read)

    def add_message(self, message, append_to=True):
        """
        Store message and if required append that to the list.

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
        """
        Check if file is already present on remote. This is used to prevent overwriting of files.

        :param path_to_remote: path to remote
        :type path_to_remote: string
        :param relative_path_to_remote_file: path to file on remote relative to the remote path
        :type relative_path_to_remote_file: string
        :param append_to: append message to messages list. By default, it is true.
        :type append_to: bool
        """

    def file_exists_locally(self, path_to_file, append_to=True):
        """
        Check if file is already present on remote. This is used to prevent overwriting of files.

        :param path_to_file: path to file
        :type path_to_file: string
        :param append_to: Append message to messages list. By default, it is true.
        :type append_to: bool
        """

        if Path(path_to_file).exists():
            self.add_message("info: " + path_to_file + " already exists", append_to)
            return True
