from shutil import copyfile
from .base import BaseRemote

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class Local(BaseRemote):
    def add(self, file_):
        with open(".surround/config.yaml", "a") as f:
            name = self.get_file_name(file_)
            f.write(name + ": " + file_ + "\n")

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
