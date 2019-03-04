import os
import unittest
import subprocess

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/01'

class InitTest(unittest.TestCase):

    def test_init(self):
        process = subprocess.run(['surround', 'init', './', '-p', 'remote', '-d', 'remote'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "Project created at " + os.getcwd() + "/remote\n")
