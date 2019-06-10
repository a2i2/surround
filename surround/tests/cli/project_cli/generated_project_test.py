import os
import shutil
from pathlib import Path
import unittest
import subprocess

class InitTest(unittest.TestCase):

    def setUp(self):
        subprocess.run(['surround', 'init', './', '-p', 'temp', '-d', 'temp', '-w', 'no'], encoding='utf-8', stdout=subprocess.PIPE)

        os.makedirs('remote')
        os.makedirs('temp/test_remote')
        Path('temp/test_remote/a.txt').touch()

    def test_run_from_subdir(self):
        process = subprocess.run(['surround', 'run'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "error: not a surround project\n")

        process = subprocess.run(['surround', 'run'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout[:31], "batch    Run batch mode locally")

        process = subprocess.run(['surround', 'run'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout[:31], "batch    Run batch mode locally")

    def test_remote_from_subdir(self):
        process = subprocess.run(['surround', 'remote'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "error: not a surround project\n")

        process = subprocess.run(['surround', 'remote'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "info: no remote found\n")

        process = subprocess.run(['surround', 'remote'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "info: no remote found\n")

        process = subprocess.run(['surround', 'remote', '-a', '-n', 'test_remote', '-u', '~', '-t', 'data'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        process = subprocess.run(['surround', 'remote'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "test_remote\n")

    def test_add_from_subdir(self):
        process = subprocess.run(['surround', 'add', 'test_remote', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "error: not a surround project\n")

        process = subprocess.run(['surround', 'add', 'test_remote', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "error: no remote named test_remote\n")

        process = subprocess.run(['surround', 'add', 'test_remote', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "error: no remote named test_remote\n")

        process = subprocess.run(['surround', 'remote', '-a', '-n', 'test_remote', '-u', 'remote', '-t', 'data'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')

        process = subprocess.run(['surround', 'add', 'test_remote', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "error: a.jpg not found.\n")

        process = subprocess.run(['surround', 'add', 'test_remote', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "error: a.jpg not found.\n")

        process = subprocess.run(['surround', 'add', 'test_remote', 'a.txt'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "info: file added successfully\n")

    def test_pull_from_subdir(self):
        process = subprocess.run(['surround', 'pull', 'test_remote', '-k', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "error: not a surround project\n")

        process = subprocess.run(['surround', 'pull', 'test_remote', '-k', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "error: no remote named test_remote\n")

        process = subprocess.run(['surround', 'pull', 'test_remote', '-k', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "error: no remote named test_remote\n")

        process = subprocess.run(['surround', 'remote', '-a', '-n', 'test_remote', '-u', 'remote', '-t', 'data'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')

        process = subprocess.run(['surround', 'pull', 'test_remote', '-k', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "error: file does not exist\n")

        process = subprocess.run(['surround', 'pull', 'test_remote', '-k', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "error: file does not exist\n")

        process = subprocess.run(['surround', 'pull', 'test_remote', '-k', 'a.txt'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "info: test_remote/a.txt already exists\n")

    def test_push_from_subdir(self):
        process = subprocess.run(['surround', 'push', 'test_remote', '-k', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "error: not a surround project\n")

        process = subprocess.run(['surround', 'push', 'test_remote', '-k', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "error: no remote named test_remote\n")

        process = subprocess.run(['surround', 'push', 'test_remote', '-k', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "error: no remote named test_remote\n")

        process = subprocess.run(['surround', 'remote', '-a', '-n', 'test_remote', '-u', 'remote', '-t', 'data'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')

        process = subprocess.run(['surround', 'push', 'test_remote', '-k', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "error: file does not exist\n")

        process = subprocess.run(['surround', 'push', 'test_remote', '-k', 'a.jpg'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "error: file does not exist\n")

        process = subprocess.run(['surround', 'push', 'test_remote', '-k', 'a.txt'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "info: a.txt pushed successfully\n")

        process = subprocess.run(['surround', 'push', 'test_remote', '-k', 'a.txt'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "info: remote/temp/a.txt already exists\n")

        process = subprocess.run(['rm', 'test_remote/a.txt'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        process = subprocess.run(['surround', 'pull', 'test_remote', '-k', 'a.txt'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "info: a.txt pulled successfully\n")

    def test_list_from_subdir(self):
        process = subprocess.run(['surround', 'list', 'test_remote'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "error: not a surround project\n")

        process = subprocess.run(['surround', 'list', 'test_remote'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "error: no remote named test_remote\n")

        process = subprocess.run(['surround', 'list', 'test_remote'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "error: no remote named test_remote\n")

        process = subprocess.run(['surround', 'remote', '-a', '-n', 'test_remote', '-u', 'remote', '-t', 'data'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')

        process = subprocess.run(['surround', 'push', 'test_remote', '-k', 'a.txt'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "info: a.txt pushed successfully\n")

        process = subprocess.run(['surround', 'list', 'test_remote'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout, "a.txt\n")

        process = subprocess.run(['surround', 'list', 'test_remote'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout, "a.txt\n")

    def tearDown(self):
        # Remove residual directories and files
        shutil.rmtree('temp')
        shutil.rmtree('remote')
