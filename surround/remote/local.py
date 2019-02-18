from .base import BaseRemote

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/18'

class Local(BaseRemote):
    def add(self, file_):
        with open(".surround/config.yaml", "a") as f:
            name = self.get_file_name(file_)
            f.write(name + ": " + file_ + "\n")

    def pull(self, file_=None):
        pass

    def push(self, file_=None):
        pass
