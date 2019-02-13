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
