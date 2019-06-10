import os
import shutil
import unittest
import subprocess

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/04'

class AddTest(unittest.TestCase):

    def test_rejecting_path(self):
        process = subprocess.run(['surround', 'init', './', '-p', 'temp', '-d', 'temp', '-w', 'no'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "info: project created at " + os.getcwd() + "/temp\n")

        is_temp = os.path.isdir(os.path.join(os.getcwd() + "/temp"))
        self.assertEqual(is_temp, True)

        process = subprocess.run(['surround', 'add', 'data', 'temp.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "error: no remote named data\n")

        process = subprocess.run(['surround', 'remote', '-a', '-n', 'data', '-u', os.getcwd(), '-t', 'data'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')

        process = subprocess.run(['surround', 'add', 'data', 'temp.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "error: temp.jpg not found.\n")

    def test_happy_path(self):
        process = subprocess.run(['surround', 'init', os.getcwd(), '-p', 'temp', '-d', 'temp', '-w', 'no'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "info: project created at " + os.getcwd() + "/temp\n")

        is_temp = os.path.isdir(os.path.join(os.getcwd() + "/temp"))
        self.assertEqual(is_temp, True)

        process = subprocess.run(['surround', 'remote', '-a', '-n', 'data', '-u', os.getcwd(), '-t', 'data'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')

        process = subprocess.run(['surround', 'add', 'data', os.getcwd() + '/surround/remote/base.py'], encoding='utf-8', stdout=subprocess.PIPE, cwd="temp")
        self.assertEqual(process.stdout, "info: file added successfully\n")

    def tearDown(self):
        # Remove residual files
        shutil.rmtree('temp')
