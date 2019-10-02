import os
import shutil
import unittest
import subprocess

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/08'

class ListTest(unittest.TestCase):

    def test_rejecting_path(self):
        process = subprocess.run(['surround', 'init', './', '-p', 'temp', '-d', 'temp', '-w', 'no'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertRegex(process.stdout, 'info: project created at .*temp\\n')

        is_temp = os.path.isdir(os.path.join(os.getcwd() + "/temp"))
        self.assertEqual(is_temp, True)

        process = subprocess.run(['surround', 'store', 'list', 'temp'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "error: no remote named temp\n")

    def test_happy_path(self):
        process = subprocess.run(['surround', 'init', './', '-p', 'temp', '-d', 'temp', '-w', 'no'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertRegex(process.stdout, 'info: project created at .*temp\\n')

        is_temp = os.path.isdir(os.path.join(os.getcwd() + "/temp"))
        self.assertEqual(is_temp, True)

        process = subprocess.run(['surround', 'store', 'remote', '-a', '-n', 'temp_remote', '-u', os.getcwd() + '/temp'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, '')

        process = subprocess.run(['surround', 'store', 'remote', '-v'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertRegex(process.stdout, 'temp_remote: .*temp\\n')

        process = subprocess.run(['surround', 'store', 'list', 'temp_remote'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertListEqual(sorted(str(process.stdout).splitlines()), sorted('config.yaml\n__main__.py\n__init__.py\nfile_system_runner.py\nweb_runner.py\nstages'.splitlines()))

    def tearDown(self):
        # Remove residual files
        shutil.rmtree('temp')
