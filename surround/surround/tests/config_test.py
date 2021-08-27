from unittest.mock import patch
import unittest
import os
from dataclasses import dataclass, field
from typing import List
from surround import BaseConfig, config as surround_config, load_config

yaml1 = """
main:
  count: 15
objects:
  - node: 43
    size: 355
enable_logging: true
"""

@dataclass
class Main:
    count: int = 0

@dataclass
class DataObject:
    node: int = 0
    size: int = 0

@surround_config(name="test_config")
@dataclass
class Config(BaseConfig):
    main: Main = Main()
    objects: List[DataObject] = field(default_factory=lambda: [])
    enable_logging: bool = False

class TestConfig(unittest.TestCase):

    def setUp(self):
        os.mkdir("temp")
        os.mkdir("temp/.surround")
        os.mkdir("temp/temp")

        with open("temp/temp/test_config.yaml", "w+") as f:
            f.write(yaml1)

        self.owd = os.getcwd()
        os.chdir("temp/")

    def tearDown(self):
        os.chdir(self.owd)

        os.unlink("temp/temp/test_config.yaml")
        os.rmdir("temp/temp")
        os.rmdir("temp/.surround")
        os.rmdir("temp")

    def test_auto_loading_project_config(self):
        config = load_config(name="test_config", config_dir=os.path.abspath('temp'), config_class=Config)
        self.assertEqual(config['main']['count'], 15)
        self.assertTrue(config['enable_logging'])
        self.assertEqual(config['objects'][0]['node'], 43)
        self.assertEqual(config['objects'][0]['size'], 355)


    def test_env_config(self):
        with patch.dict('os.environ', {'SURROUND_MAIN_COUNT': str(45)}):
            config = load_config(
                name="test_config",
                config_dir=os.path.abspath('temp'),
                config_class=Config,
                overrides=['main.count=${env:SURROUND_MAIN_COUNT}']
            )
            self.assertEqual(config["main"]["count"], 45)
