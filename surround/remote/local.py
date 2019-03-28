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

    def pull_file(self, what_to_pull, key, path_to_remote, relative_path_to_remote_file, path_to_local_file):
        path_to_remote_file = os.path.join(path_to_remote, relative_path_to_remote_file)
        copyfile(path_to_remote_file, path_to_local_file)
        return "info: " + key + " pulled successfully"

    def push_file(self, what_to_push, key, path_to_remote, relative_path_to_remote_file, path_to_local_file):
        path_to_remote_file = os.path.join(path_to_remote, relative_path_to_remote_file)
        copyfile(path_to_local_file, path_to_remote_file)
        return "info: " + key + " pushed successfully"
