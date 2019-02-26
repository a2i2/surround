import os
from pathlib import Path
from shutil import copyfile
from .base import BaseRemote

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class Local(BaseRemote):
    def add(self, add_to, file_):
        # Check file is valid
        f = Path(file_)
        if f.is_file():
            name = self.get_file_name(file_)
            project_name = self.read_from_local_config("project-info", "project-name")
            path_to_remote = self.read_from_config("remote", add_to)

            if path_to_remote:
                # Append filename
                path_to_file = path_to_remote + "/" + project_name + "/" + name
                self.write_config(add_to, ".surround/config.yaml", name, path_to_file)
                return "File added successfully"
            else:
                return "No remote named " + path_to_remote
        else:
            return file_ + " not found"

    def pull(self, what_to_pull, file_=None):
        if file_:
            file_to_pull = self.read_from_config(what_to_pull, file_)
            if file_to_pull:
                copyfile(file_to_pull, what_to_pull + '/' + file_)
                return "File pulled successfully"
            else:
                return "File not added, add that by surround add"
        else:
            """
            Add code to pull all files
            """

    def push(self, what_to_push, file_=None):
        if file_:
            filename = self.get_file_name(file_)
            file_to_push = self.read_from_config(what_to_push, filename)
            os.makedirs(os.path.dirname(file_to_push), exist_ok=True)
            if file_to_push:
                copyfile(what_to_push + '/' + filename, file_to_push)
                return "File pushed successfully"
            else:
                return "File not added, add that by surround add"
        else:
            """
            Add code to push all files
            """
