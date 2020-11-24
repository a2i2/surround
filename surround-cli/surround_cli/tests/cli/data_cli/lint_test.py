import os
import shutil
import unittest
import subprocess

from surround_cli.data.container import DataContainer

class LintDataContainerTest(unittest.TestCase):
    def setUp(self):
        os.makedirs('temp/test_group')

        for i in range(100):
            with open("temp/test_group/%i.png" % i, "w+") as f:
                f.write('test data')

        for i in range(20):
            with open("temp/derp_%i.jpg" % i, "w+") as f:
                f.write("test data 2")

        container = DataContainer()
        container.import_directory('temp/')
        container.metadata.set_property("summary.title", "Test title")
        container.metadata.set_property("summary.creator", "Test name")
        container.metadata.set_property("summary.description", "Test description")
        container.metadata.set_property("summary.publisher", "Test publisher")
        container.metadata.set_property("summary.contributor", "Test contributor")
        container.metadata.set_property("summary.subject", ["test", "subject", "list"])
        container.metadata.set_property("summary.language", "en")
        container.metadata['manifests'][0]['description'] = "Test group description"
        container.metadata['manifests'][0]['language'] = 'en'
        container.export('temp.data.zip')

    def tearDown(self):
        shutil.rmtree('temp')

        if os.path.exists("temp.data.zip"):
            os.remove("temp.data.zip")

    def test_happy_path(self):
        process = subprocess.Popen(['surround', 'data', 'lint', 'temp.data.zip'], encoding='utf-8', stdout=subprocess.PIPE)
        process.wait()

        output = process.stdout.read()

        self.assertIn("3/3 checks passed!", output)
        self.assertIn("Your container looks good.", output)

        process.stdout.close()
