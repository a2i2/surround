import os
import unittest
import subprocess

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/01'

class RemoteTest(unittest.TestCase):

    def test_remote(self):
        process = subprocess.run(['surround', 'remote'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "error: not a surround project\nerror: goto project root directory\n")

        process = subprocess.run(['surround', 'init', './', '-p', 'remote', '-d', 'remote'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "Project created at " + os.getcwd() + "/remote\n")

        process = subprocess.run(['surround', 'remote'], encoding='utf-8', stdout=subprocess.PIPE, cwd='remote')
        self.assertEqual(process.stdout, "info: no remote found\n")
