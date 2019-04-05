import unittest
import subprocess

class InitTest(unittest.TestCase):

    def setUp(self):
        subprocess.run(['surround', 'init', './', '-p', 'temp', '-d', 'temp'], encoding='utf-8', stdout=subprocess.PIPE)

    def test_run_from_subdir(self):
        process = subprocess.run(['surround', 'run'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertEqual(process.stdout, "error: not a surround project\n")

        process = subprocess.run(['surround', 'run'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp')
        self.assertEqual(process.stdout[:55], "build    Build the Docker image for the current project")

        process = subprocess.run(['surround', 'run'], encoding='utf-8', stdout=subprocess.PIPE, cwd='temp/temp')
        self.assertEqual(process.stdout[:55], "build    Build the Docker image for the current project")

    def tearDown(self):
        # Remove residual files
        subprocess.run(['rm', '-r', './temp'], encoding='utf-8', stdout=subprocess.PIPE)
