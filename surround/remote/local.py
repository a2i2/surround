from pathlib import Path
from shutil import copyfile
import yaml
from .base import BaseRemote

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class Local(BaseRemote):
    def add(self, add_to, file_):
        name = self.get_file_name(file_)

        with open(".surround/config.yaml", "r") as f:
            read_config = yaml.load(f) or {}

        if "remote" in read_config and add_to in read_config["remote"]:
            # Append filename
            path_to_file = read_config["remote"][add_to] + "/" + name
            self.write_config(add_to, ".surround/config.yaml", name, path_to_file)
            return "File added successfully"
        else:
            home = str(Path.home())

            if Path(home + "/.surround/config.yaml").exists():
                if "remote" in read_config and add_to in read_config["remote"]:
                    # Append filename
                    path_to_file = read_config["remote"][add_to] + "/" + name
                    self.write_config(add_to, home + "/.surround/config.yaml", name, path_to_file)
                    return "File added successfully"
                else:
                    return "No remote named" + add_to
            else:
                return "No remote named" + add_to

    def pull(self, what_to_pull, file_=None):
        if file_:
            file_to_pull = self.read_from_config(what_to_pull, file_)
            if file_to_pull:
                copyfile(file_to_pull, 'data/input/' + file_)
            else:
                print("File not added")
                print("Add that by surround add")
        else:
            pass


    def push(self, what_to_push, file_=None):
        if file_:
            file_to_push = self.read_from_config(what_to_push, file_)
            if file_to_push:
                copyfile('data/input/' + file_, file_to_push)
            else:
                print("File not added")
                print("Add that by surround add")
        else:
            pass
