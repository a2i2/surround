import os
from pathlib import Path
from shutil import copyfile
import yaml
from .base import BaseRemote

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class Local(BaseRemote):
    def add(self, add_to, file_):
        # Check file is valid
        f = Path(file_)
        if f.is_file():
            name = self.get_file_name(file_)

            with open(".surround/config.yaml", "r") as f:
                read_config = yaml.load(f) or {}
                project_name = read_config["project-info"]['project-name']

            if "remote" in read_config and add_to in read_config["remote"]:
                # Append filename
                path_to_file = read_config["remote"][add_to] + "/" + project_name + "/" + name
                self.write_config(add_to, ".surround/config.yaml", name, path_to_file)
                return "File added successfully"
            else:
                home = str(Path.home())

                if Path(home + "/.surround/config.yaml").exists():
                    if "remote" in read_config and add_to in read_config["remote"]:
                        # Append filename
                        path_to_file = read_config["remote"][add_to] + "/" + project_name + "/" + name
                        self.write_config(add_to, home + "/.surround/config.yaml", name, path_to_file)
                        return "File added successfully"
                    else:
                        return "No remote named" + add_to
                else:
                    return "No remote named" + add_to
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
