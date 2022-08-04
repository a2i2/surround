import os
import shutil
import unittest
import subprocess

from surround_cli.data.container import DataContainer


class InspectDataContainerTest(unittest.TestCase):
    def setUp(self):
        os.makedirs("temp/test_group")

        for i in range(100):
            with open("temp/test_group/%i.png" % i, "w+") as f:
                f.write("test data")

        for i in range(20):
            with open("temp/derp_%i.jpg" % i, "w+") as f:
                f.write("test data 2")

        container = DataContainer()
        container.import_directory("temp/")
        container.metadata.set_property("summary.title", "Test title")
        container.metadata.set_property("summary.creator", "Test name")
        container.metadata.set_property("summary.description", "Test description")
        container.metadata.set_property("summary.publisher", "Test publisher")
        container.metadata.set_property("summary.contributor", "Test contributor")
        container.metadata.set_property("summary.subject", ["test", "subject", "list"])
        container.export("temp.data.zip")

    def tearDown(self):
        shutil.rmtree("temp")

        if os.path.exists("temp.data.zip"):
            os.remove("temp.data.zip")

    def test_happy_path(self):
        process = subprocess.Popen(
            ["surround", "data", "inspect", "temp.data.zip"],
            encoding="utf-8",
            stdout=subprocess.PIPE,
        )
        process.wait()

        output = process.stdout.read()

        self.assertIn("Test title", output)
        self.assertIn("Test name", output)
        self.assertIn("Test description", output)
        self.assertIn("Test publisher", output)
        self.assertIn("Test contributor", output)
        self.assertIn("'test'", output)
        self.assertIn("'subject'", output)
        self.assertIn("'list'", output)

        for i in range(100):
            self.assertIn("test_group/%i.png" % i, output)

        for i in range(20):
            self.assertIn("derp_%i.jpg" % i, output)

        process.stdout.close()
