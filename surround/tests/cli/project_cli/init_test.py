import os
import shutil
import unittest
import subprocess

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/01'

class InitTest(unittest.TestCase):

    def test_happy_path(self):
        process = subprocess.run(['surround', 'init', './', '-p', 'temp', '-d', 'temp', '-w', 'no'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "info: project created at " + os.getcwd() + "/temp\n")

        is_temp = os.path.isdir(os.path.join(os.getcwd() + "/temp"))
        self.assertEqual(is_temp, True)

        process = subprocess.run(['surround', 'init', './', '-p', 'temp', '-d', 'temp', '-w', 'no'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "error: directory ./temp already exists\n")

    def tearDown(self):
        # Remove residual files
        shutil.rmtree('temp')
