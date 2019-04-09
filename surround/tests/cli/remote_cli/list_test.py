import os
import shutil
import unittest
import subprocess

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/08'

class ListTest(unittest.TestCase):

    def test_rejecting_path(self):
        process = subprocess.run(['surround', 'init', './', '-p', 'temp', '-d', 'temp'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "info: project created at " + os.getcwd() + "/temp\n")

        is_temp = os.path.isdir(os.path.join(os.getcwd() + "/temp"))
        self.assertEqual(is_temp, True)

        process = subprocess.run(['surround', 'list', 'temp'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "error: no remote named temp\n")

    def test_happy_path(self):
        process = subprocess.run(['surround', 'init', './', '-p', 'temp', '-d', 'temp'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "info: project created at " + os.getcwd() + "/temp\n")

        is_temp = os.path.isdir(os.path.join(os.getcwd() + "/temp"))
        self.assertEqual(is_temp, True)

        process = subprocess.run(['surround', 'remote', '-a', '-n', 'temp_remote', '-u', os.getcwd() + '/temp', '-t', 'data'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, '')

        process = subprocess.run(['surround', 'remote', '-v'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, 'temp_remote: ' + os.getcwd() + '/temp\n')

        process = subprocess.run(['surround', 'list', 'temp_remote'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertListEqual(sorted(str(process.stdout).splitlines()), sorted('config.yaml\nstages.py\n__main__.py\n__init__.py\nwrapper.py\n'.splitlines()))

    def tearDown(self):
        # Remove residual files
        shutil.rmtree('temp')
