import os
import unittest
import subprocess

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/08'

class AddTest(unittest.TestCase):

    def test_rejecting_path(self):
        process = subprocess.run(['surround', 'init', './', '-p', 'temp', '-d', 'temp'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "Project created at " + os.getcwd() + "/temp\n")

        is_temp = os.path.isdir(os.path.join(os.getcwd() + "/temp"))
        self.assertEqual(is_temp, True)

        process = subprocess.run(['surround', 'list', 'temp'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "error: no remote named temp\n")

    def tearDown(self):
        # Remove residual files
        subprocess.run(['rm', '-r', './temp'], encoding='utf-8', stdout=subprocess.PIPE)
