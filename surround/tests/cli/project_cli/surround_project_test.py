import unittest
import subprocess

class InitTest(unittest.TestCase):

    def setUp(self):
        subprocess.run(['surround', 'init', './', '-p', 'temp', '-d', 'temp'], encoding='utf-8', stdout=subprocess.PIPE)

        subprocess.run(['mkdir', 'remote'], encoding='utf-8', stdout=subprocess.PIPE)
        subprocess.run(['mkdir', 'test_remote'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        subprocess.run(['touch', 'a.txt'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/test_remote')

    def test_run_from_subdir(self):
        process = subprocess.run(['surround', 'run'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "error: not a surround project\n")

        process = subprocess.run(['surround', 'run'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout[:55], "build    Build the Docker image for the current project")

        process = subprocess.run(['surround', 'run'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout[:55], "build    Build the Docker image for the current project")

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

    def tearDown(self):
        # Remove residual directories and files
        subprocess.run(['rm', '-r', './temp'], encoding='utf-8', stdout=subprocess.PIPE)
        subprocess.run(['rm', '-r', './remote'], encoding='utf-8', stdout=subprocess.PIPE)
