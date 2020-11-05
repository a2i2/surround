from unittest.mock import patch
import unittest
import os
import tempfile
import yaml
from surround import Config

yaml1 = """
main:
  surround: au.com.first_stage.FirstStage
  count: 3

objects:
  - node: 3
    size: 4
  - node: 8
    size: 15
"""

yaml2 = """
main:
  count: 15

objects:
  - node: 43
    size: 355

enable_logging: true
"""

yaml3 = """
main:
  count: 15
"""


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.f1 = tempfile.NamedTemporaryFile(delete=False)
        self.f1.write(str.encode(yaml1))
        self.f1.close()

        self.f2 = tempfile.NamedTemporaryFile(delete=False)
        self.f2.write(str.encode(yaml2))
        self.f2.close()

        os.mkdir("temp")
        os.mkdir("temp/.surround")
        os.mkdir("temp/temp")

        with open("temp/temp/config.yaml", "w+") as f:
            f.write(yaml2)

        self.owd = os.getcwd()
        os.chdir("temp/")

    def tearDown(self):
        os.unlink(self.f1.name)
        os.unlink(self.f2.name)

        os.chdir(self.owd)

        os.unlink("temp/temp/config.yaml")
        os.rmdir("temp/temp")
        os.rmdir("temp/.surround")
        os.rmdir("temp")

    def test_auto_loading_project_config(self):
        config = Config(auto_load=True)
        self.assertEqual(config['main']['count'], 15)
        self.assertTrue(config['enable_logging'])
        self.assertIsInstance(config['objects'], list)
        self.assertEqual(config['objects'][0]['node'], 43)
        self.assertEqual(config['objects'][0]['size'], 355)

    def test_merging_config(self):
        config = Config()
        config.read_config_files([self.f1.name, self.f2.name])
        output = {
            'company': 'a2i2',
            'version': 'latest',
            'image': 'surround',
            'surround': {
                'enable_stage_output_dump': False
            },
            'main': {
                'surround': 'au.com.first_stage.FirstStage',
                'count': 15
            },
            'objects': [{
                'node': 43,
                'size': 355
            }],
            'enable_logging': True
        }
        self.assertDictEqual(config.__dict__["_storage"], output)


    def test_env_config(self):
        with patch.dict('os.environ', {
                'SURROUND_MAIN_COUNT': str(45),
                'SURROUND_TEMP': str(0.3),
                'SURROUND_STRING': "this is a test string",
                'SURROUND_BOOL': "true",
                'SURROUND_BOOLTWO': "false",
                "SURROUND_BOOLTHREE": "True",
                "SURROUND_BOOLFOUR": "False"
        }):
            config = Config()
            config.read_from_dict(yaml.safe_load(yaml3))
            self.assertEqual(config["main"]["count"], 45)
            self.assertEqual(config["temp"], 0.3)
            self.assertEqual(config["string"], "this is a test string")
            self.assertTrue(config["bool"])
            self.assertFalse(config["booltwo"])
            self.assertTrue(config["boolthree"])
            self.assertFalse(config["boolfour"])
