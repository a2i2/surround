import os
import shutil
import unittest
import subprocess

from surround_cli.remote.local import Local

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/04'

class AddTest(unittest.TestCase):

    def test_rejecting_path(self):
        process = subprocess.run(['surround', 'init', './', '-p', 'temp', '-d', 'temp', '-n', 'Stefanus Kurniawan', '-e', 'stefanus.kurniawan@deakin.edu.au', '-w', 'False'],
                                 encoding='utf-8', stdout=subprocess.PIPE, check=True)
        self.assertIn("info: project created at", process.stdout)
        self.assertIn("temp", process.stdout)

        is_temp = os.path.isdir(os.path.join(os.getcwd() + "/temp"))
        self.assertEqual(is_temp, True)

        local_remote = Local()

        os.chdir("temp")
        result = local_remote.add('data', 'temp.jpg')
        os.chdir("../")
        self.assertEqual(result, "error: no remote named data")

        process = subprocess.run(['surround', 'store', 'remote', '-a', '-n', 'data', '-u', os.getcwd()], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp', check=True)

        os.chdir("temp")
        result = local_remote.add('data', 'temp.jpg')
        os.chdir("../")
        self.assertEqual(result, "error: temp.jpg not found.")

    def test_happy_path(self):
        process = subprocess.run(['surround', 'init', os.getcwd(), '-p', 'temp', '-d', 'temp', '-n', 'Stefanus Kurniawan', '-e', 'stefanus.kurniawan@deakin.edu.au', '-w', 'False'],
                                 encoding='utf-8', stdout=subprocess.PIPE, check=True)
        self.assertIn("info: project created at", process.stdout)
        self.assertIn("temp", process.stdout)

        is_temp = os.path.isdir(os.path.join(os.getcwd() + "/temp"))
        self.assertEqual(is_temp, True)

        process = subprocess.run(['surround', 'store', 'remote', '-a', '-n', 'data', '-u', os.getcwd()], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp', check=True)

        local_remote = Local()

        os.chdir("temp")
        result = local_remote.add('data', os.path.join(os.getcwd(), '..', 'surround_cli/remote/base.py'))
        os.chdir("../")

        self.assertEqual(result, "info: file added successfully")

    def tearDown(self):
        # Remove residual files
        shutil.rmtree('temp')
