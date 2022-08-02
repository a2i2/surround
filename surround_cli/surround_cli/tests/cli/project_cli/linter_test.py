import unittest
import shutil
import subprocess

class LinterTest(unittest.TestCase):
    def setUp(self):
        """
        Generate a temp project
        """

        process = subprocess.Popen(['surround', 'init', '-p', 'test_proj', '-d', 'testing', '-n', 'Stefanus Kurniawan', '-e', 'stefanus.kurniawan@deakin.edu.au', '-w', 'True'],
                                   encoding='utf-8', stdout=subprocess.PIPE)
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

        process = subprocess.Popen(['surround', 'lint'], cwd='test_proj/', encoding='utf-8', stdout=subprocess.PIPE)
        output = process.communicate()[0]

        # Linter should be able to locate .surround folder if project valid
        self.assertNotIn(".surround does not exist", output, "Current directory not a Surround project")
        self.assertIn("Your code has been rated at 10.00/10", output, "The generated code is not lint error free!")

    def test_lint_invalid_project(self):
        """
        Test the linter on an invalid project
        """

        process = subprocess.Popen(['surround', 'lint'], cwd='.', encoding='utf-8', stdout=subprocess.PIPE)
        output = process.communicate()[0]

        # Linter won't be able to find .surround when attempting to lint an invalid dir
        self.assertIn(".surround does not exist", output)
