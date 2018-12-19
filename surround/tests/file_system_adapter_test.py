import unittest
from surround import FileSystemAdapter, Pipeline
import sys
import io
import os


class MyFileSystemAdapter(FileSystemAdapter):

    def transform(self, args):
        pass

class TestFileSystemAdapter(unittest.TestCase):

    def test_file_system_adapter_validation(self):
        with self.assertRaises(AssertionError):
            FileSystemAdapter("3")

        with self.assertRaises(AssertionError):
            FileSystemAdapter(Pipeline([]))

        with self.assertRaises(AssertionError):
            FileSystemAdapter(Pipeline([]), file0=3)

    def test_file_system_adapter_parser(self):
        fs = MyFileSystemAdapter(Pipeline([]),
                                 description="A test set up",
                                 config_file="System configuration file",
                                 file0="Input file",
                                 file1="Input file",
                                 file2="Input file"
        )
        path = os.path.join(os.path.dirname(__file__), "config.cfg")
        fs.parser.parse_args(['-f0', path, '-f1', path, '-f2', path, '-c', path])
