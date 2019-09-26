import os
import shutil
import unittest
from ..experiment.file_storage_driver import FileStorageDriver

class FileStorageDriverTest(unittest.TestCase):
    def setUp(self):
        os.mkdir("test_remote")
        os.mkdir("test_remote/test_folder")
        os.mkdir("temp")

        with open("test_remote/test.txt", "w+") as f:
            f.write("TEST_DATA")

        with open("test_remote/test_folder/test.txt", "w+") as f:
            f.write("TEST_DATA_2")

        with open("temp/another_test.txt", "w+") as f:
            f.write("MORE_TEST_DATA")

    def tearDown(self):
        shutil.rmtree("test_remote")
        shutil.rmtree("temp")

    def test_invalid_path(self):
        with self.assertRaises(OSError):
            FileStorageDriver("adj#k:?jdl")

    def test_location_create(self):
        FileStorageDriver("test_remote/another_remote")
        self.assertTrue(os.path.exists("test_remote/another_remote"))

    def test_push_data(self):
        storage = FileStorageDriver("test_remote")
        storage.push("test_data.txt", bytes_data="DATA".encode("utf-8"))

        self.assertTrue(os.path.exists("test_remote/test_data.txt"))

        with open("test_remote/test_data.txt", "r") as f:
            self.assertEqual("DATA", f.read())

    def test_pull_data(self):
        storage = FileStorageDriver("test_remote")
        data = storage.pull("test.txt")

        self.assertEqual("TEST_DATA", data.decode('utf-8'))

    def test_push_file(self):
        storage = FileStorageDriver("test_remote")
        storage.push("another_test.txt", local_path="temp/another_test.txt")

        self.assertTrue(os.path.exists("test_remote/another_test.txt"))

        with open("test_remote/another_test.txt", "r") as f:
            self.assertEqual("MORE_TEST_DATA", f.read())

    def test_pull_file(self):
        storage = FileStorageDriver("test_remote")
        storage.pull("test.txt", local_path="temp/test.txt")

        self.assertTrue(os.path.exists("temp/test.txt"))

        with open("temp/test.txt", "r") as f:
            self.assertEqual("TEST_DATA", f.read())

    def test_push_no_override(self):
        storage = FileStorageDriver("test_remote")

        with self.assertRaises(FileExistsError):
            storage.push("test.txt", local_path="temp/another_test.txt", override_ok=False)

    def test_pull_no_override(self):
        storage = FileStorageDriver("test_remote")

        with self.assertRaises(FileExistsError):
            storage.pull("test.txt", local_path="temp/another_test.txt", override_ok=False)

    def test_push_override(self):
        storage = FileStorageDriver("test_remote")
        storage.push("test.txt", local_path="temp/another_test.txt", override_ok=True)

        with open("test_remote/test.txt", "r") as f:
            self.assertEqual("MORE_TEST_DATA", f.read())

    def test_pull_override(self):
        storage = FileStorageDriver("test_remote")
        storage.pull("test.txt", local_path="temp/another_test.txt", override_ok=True)

        with open("temp/another_test.txt", "r") as f:
            self.assertEqual("TEST_DATA", f.read())

    def test_exists(self):
        storage = FileStorageDriver("test_remote")
        self.assertTrue(storage.exists("test.txt"))
        self.assertFalse(storage.exists("non_exist.txt"))

    def test_get_files(self):
        storage = FileStorageDriver("test_remote")

        files = {f.replace('\\', '/') for f in storage.get_files()}
        expected = {"test.txt", "test_folder/test.txt"}

        self.assertEqual(expected, files)

    def test_get_files_from_dir(self):
        storage = FileStorageDriver("test_remote")

        files = {f.replace('\\', '/') for f in storage.get_files(base_url="test_folder")}
        expected = {"test.txt"}

        self.assertEqual(expected, files)

    def test_delete_file(self):
        storage = FileStorageDriver("test_remote")
        storage.delete("test.txt")

        self.assertFalse(os.path.exists("test_remote/test.txt"))
        self.assertFalse(storage.exists("test.txt"))

    def test_delete_folder(self):
        storage = FileStorageDriver("test_remote")
        storage.delete("test_folder")

        self.assertFalse(os.path.exists("test_remote/test_folder"))
        self.assertFalse(storage.exists("test_folder"))

    def test_delete_invalid_path(self):
        storage = FileStorageDriver("test_remote")

        with self.assertRaises(FileNotFoundError):
            storage.delete("non_exist.txt")
