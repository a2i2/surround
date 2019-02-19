from shutil import copyfile
from surround.config import Config
from .base import BaseRemote

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class Local(BaseRemote):
    def add(self, file_):
        with open(".surround/config.yaml", "a") as f:
            name = self.get_file_name(file_)
            f.write(name + ": " + file_ + "\n")

    def pull(self, file_=None):
        config = Config()

        # Get file to pull
        config.read_config_files([".surround/config.yaml"])
        file_to_pull = config[file_]
        copyfile(file_to_pull, 'data/input/' + file_)

    def push(self, file_=None):
        pass
