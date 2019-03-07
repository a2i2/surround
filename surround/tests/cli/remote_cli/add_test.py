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

        process = subprocess.run(['surround', 'remote', '-a', '-n', 'data', '-u', os.getcwd(), '-t', 'data'], encoding='utf-8', stdout=subprocess.PIPE, cwd='add')

        process = subprocess.run(['surround', 'add', 'data', 'temp.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='add')
        self.assertEqual(process.stdout, "error: temp.jpg not found.\n")

        is_add = os.path.isdir(os.path.join(os.getcwd() + "/add"))
        self.assertEqual(is_add, True)

        # Remove residual files
        subprocess.run(['rm', '-r', './add'], encoding='utf-8', stdout=subprocess.PIPE)

        is_add = os.path.isdir(os.path.join(os.getcwd() + "/add"))
        self.assertEqual(is_add, False)

    def test_happy_path(self):
        process = subprocess.run(['surround', 'init', os.getcwd(), '-p', 'addd', '-d', 'addd'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "Project created at " + os.getcwd() + "/addd\n")

        is_addd = os.path.isdir(os.path.join(os.getcwd() + "/addd"))
        self.assertEqual(is_addd, True)

        process = subprocess.run(['surround', 'remote', '-a', '-n', 'data', '-u', os.getcwd(), '-t', 'data'], encoding='utf-8', stdout=subprocess.PIPE, cwd='addd')

        process = subprocess.run(['surround', 'add', 'data', os.getcwd() + '/surround/remote/base.py'], encoding='utf-8', stdout=subprocess.PIPE, cwd="addd")
        self.assertEqual(process.stdout, "info: file added successfully\n")

        # Remove residual files
        subprocess.run(['rm', '-r', './addd'], encoding='utf-8', stdout=subprocess.PIPE)

        is_addd = os.path.isdir(os.path.join(os.getcwd() + "/addd"))
        self.assertEqual(is_addd, False)
