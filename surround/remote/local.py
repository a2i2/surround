import os
from pathlib import Path
from shutil import copyfile
from .base import BaseRemote

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class Local(BaseRemote):
    def add(self, add_to, key):
        project_name = self.read_from_local_config("project-info", "project-name")
        path_to_local_file = Path("data/" + key)
        path_to_remote = self.read_from_config("remote", add_to)
        if path_to_remote:
            # Append filename
            path_to_remote_file = path_to_remote + "/" + project_name + "/" + key
            if Path(path_to_local_file).is_file() or Path(path_to_remote_file).is_file():
                self.write_config(add_to, ".surround/config.yaml", key, path_to_remote_file)
                return "info: file added successfully"
            else:
                return "error: " + key + " not found."
        else:
            return "error: no remote named " + add_to

    def pull(self, what_to_pull, key=None):
        if key:
            file_to_pull = self.read_from_config(what_to_pull, key)
            if file_to_pull:
                copyfile(file_to_pull, what_to_pull + '/' + key)
                return "File pulled successfully"
            else:
                return "File not added, add that by surround add"
        else:
            """
            Add code to pull all files
            """

    def push(self, what_to_push, key=None):
        if key:
            file_to_push = self.read_from_config(what_to_push, key)
            os.makedirs(os.path.dirname(file_to_push), exist_ok=True)
            if file_to_push:
                copyfile(what_to_push + '/' + key, file_to_push)
                return "File pushed successfully"
            else:
                return "File not added, add that by surround add"
        else:
            """
            Add code to push all files
            """
