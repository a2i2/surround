import os
import json
from shutil import copyfile

'''
Handles file I/O
'''

__author__ = 'Akshat Bajaj'
__date__ = '2019/02/14'

'''
    Write remote to file

    @param {str} filename: file to write
    @param {str} name: name of the remote
    @param {str} path: path to the remote
'''
def write_remote_to_file(filename, name, path):
    file_ = open(filename, "a")
    file_.write("\n")
    file_.write(name + " = " + path)
    file_.close()

def read_file(filename):
    with open(filename) as json_file:
        data = json.load(json_file)
        json_file.close()

    return data

def pull_data(file_):
    input_file = read_file(file_)
    filename = os.path.splitext(os.path.basename(file_))[0]

    copyfile("/Users/akshat/Desktop/esolutions/" + input_file['dir-name'] + "/" + filename, os.path.splitext(file_)[0])
