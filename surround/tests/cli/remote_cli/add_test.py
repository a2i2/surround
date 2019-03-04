import os
import unittest
import subprocess

__author__ = 'Akshat Bajaj'
__date__ = '2019/03/04'

class AddTest(unittest.TestCase):

    def test_rejecting_path(self):
        process = subprocess.run(['surround', 'init', './', '-p', 'add', '-d', 'add'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "Project created at " + os.getcwd() + "/add\n")

        process = subprocess.run(['surround', 'add', 'data', 'temp.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='add')
        self.assertEqual(process.stdout, "error: no remote named data\n")

        process = subprocess.run(['surround', 'remote', '-a', '-n', 'data', '-u', os.getcwd()], encoding='utf-8', stdout=subprocess.PIPE, cwd='add')

        process = subprocess.run(['surround', 'add', 'data', 'temp.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='add')
        self.assertEqual(process.stdout, "error: temp.jpg not found.\n")
