from shutil import copyfile
from .base import BaseRemote

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class Local(BaseRemote):
    def add(self, file_):
        with open(".surround/config.yaml", "a") as f:
            name = self.get_file_name(file_)
            f.write(name + ": " + file_ + "\n")

    def pull(self, file_=None):
        file_to_pull = self.read_data_from_surround_local_config(file_)
        copyfile(file_to_pull, 'data/input/' + file_)

    def push(self, file_=None):
        file_to_push = self.read_data_from_surround_local_config(file_)
        copyfile('data/input/' + file_, file_to_push)
