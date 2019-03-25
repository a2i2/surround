import os
from pathlib import Path
from shutil import copyfile
from .base import BaseRemote

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class Local(BaseRemote):

    def file_exists_on_remote(self, path_to_remote_file, append_to=True):
        """For local remote, just check whether file is present locally

        :param path_to_remote_file: path to file
        :type path_to_remote_file: str
        :param append_to: Append message to messages list. By default, it is true.
        :type append_to: bool
        """
        return self.file_exists_locally(path_to_remote_file, append_to)

    def add(self, add_to, key):
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
                copyfile(file_to_pull, path_to_pulled_file)
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

    def push(self, what_to_push, key=None):
        project_name = self.get_project_name()
        if project_name is None:
            return self.messages

        if key:
            path_to_remote = self.read_from_config("remote", what_to_push)
            path_to_remote_file = os.path.join(path_to_remote, project_name, key)

            if self.file_exists_on_remote(path_to_remote_file):
                return self.message

            path_to_local_file = os.path.join(what_to_push, key)
            os.makedirs(os.path.dirname(path_to_remote_file), exist_ok=True)
            if path_to_remote_file and self.file_exists_locally(path_to_local_file, False):
                copyfile(os.path.join(what_to_push, key), path_to_remote_file)
                self.add_message("info: " + key + " pushed successfully")
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
