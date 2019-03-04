import os
import unittest
import subprocess

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/01'

class InitTest(unittest.TestCase):

    def test_happy_path(self):
        process = subprocess.run(['surround', 'init', './', '-p', 'remote', '-d', 'remote'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "Project created at " + os.getcwd() + "/remote\n")

    def test_rejecting_path(self):
        process = subprocess.run(['surround', 'init', './', '-p', 'remote', '-d', 'remote'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "Directory ./remote already exists\n")
