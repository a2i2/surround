import os
import shutil
import unittest
import subprocess

from surround.data.container import DataContainer

class CreateDataContainerTest(unittest.TestCase):
    def setUp(self):
        os.makedirs('temp/test_group')

        for i in range(100):
            with open("temp/test_group/%i.png" % i, "w+") as f:
                f.write('test data')

        for i in range(20):
            with open("temp/derp_%i.jpg" % i, "w+") as f:
                f.write("test data 2")

    def tearDown(self):
        shutil.rmtree('temp')

        if os.path.exists("temp.data.zip"):
            os.remove("temp.data.zip")

    def test_happy_path(self):
        std_input = "Test name\n"
        std_input += "Test title\n"
        std_input += "Test description\n"
        std_input += "Test publisher\n"
        std_input += "Test contributor\n"
        std_input += "2019-02-03T24:00\n"
        std_input += "test,subject,list\n"
        std_input += "1\n"
        std_input += "1\n"
        std_input += "n\n"
        std_input += "\n"
        std_input += "\n"
        std_input += "\n"
        std_input += "Test group description\n"
        std_input += "1\n"

        process = subprocess.run(['surround', 'data', 'create', '-d', 'temp', '-o', 'temp.data.zip'], input=std_input, encoding='ascii', check=True)

        self.assertEqual(process.returncode, 0)
        self.assertTrue(os.path.exists("temp.data.zip"))

        # Get the metadata from the container file
        container = DataContainer('temp.data.zip')
        metadata = container.metadata

        self.assertEqual(metadata['summary']['creator'], "Test name")
        self.assertEqual(metadata['summary']['title'], "Test title")
        self.assertEqual(metadata['summary']['description'], "Test description")
        self.assertEqual(metadata['summary']['publisher'], "Test publisher")
        self.assertEqual(metadata['summary']['contributor'], "Test contributor")
        self.assertIn('test', metadata['summary']['subject'])
        self.assertIn('subject', metadata['summary']['subject'])
        self.assertIn('list', metadata['summary']['subject'])
        self.assertEqual(metadata['summary']['language'], "en")
        self.assertEqual(metadata['summary']['date'], "2019-02-03T24:00")
        self.assertIn('image/png', metadata['summary']['formats'])
        self.assertIn('image/jpeg', metadata['summary']['formats'])

        self.assertEqual(metadata['manifests'][0]['path'], "test_group")
        self.assertEqual(metadata['manifests'][0]['description'], "Test group description")
        self.assertIn('image/png', metadata['manifests'][0]['formats'])
        self.assertNotIn('image/jpeg', metadata['manifests'][0]['formats'])

        self.assertTrue(all([container.file_exists("test_group/%i.png" % i) for i in range(100)]))
        self.assertTrue(all([container.file_exists("derp_%i.jpg" % i) for i in range(20)]))
