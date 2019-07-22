import unittest
import shutil
import subprocess

class LinterTest(unittest.TestCase):
    def setUp(self):
        """
        Generate a temp project
        """

        process = subprocess.Popen(['surround', 'init', '-p', 'test_proj', '-d', 'testing', '-w', 'y'], encoding='utf-8', stdout=subprocess.PIPE)
        self.assertIn('info: project created', process.communicate()[0])

    def tearDown(self):
        """
        Delete the temp project
        """

        shutil.rmtree('test_proj')

    def test_lint_valid_project(self):
        """
        Test the linter on a valid project
        """

        process = subprocess.Popen(['surround', 'lint', '-p', 'y'], cwd='test_proj/', encoding='utf-8', stdout=subprocess.PIPE)
        output = process.communicate()[0]

        # Linter should be able to locate .surround folder if project valid
        self.assertNotIn(".surround does not exist", output, "Current directory not a Surround project")

    def test_lint_invalid_project(self):
        """
        Test the linter on an invalid project
        """

        process = subprocess.Popen(['surround', 'lint', '-p', 'y'], cwd='.', encoding='utf-8', stdout=subprocess.PIPE)
        output = process.communicate()[0]

        # Linter won't be able to find .surround when attempting to lint an invalid dir
        self.assertIn(".surround does not exist", output)
