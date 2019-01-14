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

    def tearDown(self):
        os.unlink(self.f1.name)
        os.unlink(self.f2.name)

    def test_merging_config(self):

        config = Config()
        config.read_config_files([self.f1.name, self.f2.name])
        output = {
            'surround' : {
                "stages" : False,
            },
            'main': {
                'count': 15,
                'surround': 'au.com.first_stage.FirstStage'
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
                'SURROUND_TEMP': str(0.3)
        }):
            config = Config()
            config.read_from_dict(yaml.safe_load(yaml3))
            self.assertEqual(config["main"]["count"], 45)
            self.assertEqual(config["temp"], 0.3)
