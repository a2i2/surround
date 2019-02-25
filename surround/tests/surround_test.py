import unittest
import os
from surround import Surround, Stage, SurroundData, Config
from .stages.first_stage import FirstStage

class HelloStage(Stage):
    def operate(self, surround_data, config):
        surround_data.text = "hello"
        if "helloStage" in config:
            surround_data.config_value = config["helloStage"]["suffix"]

class BasicData(SurroundData):
    text = None
    config_value = None
    stage1 = None
    stage2 = None

class TestSurround(unittest.TestCase):

    def test_happy_path(self):
        surround = Surround([HelloStage()])
        data = BasicData()
        surround.process(data)
        self.assertEqual(data.text, "hello")

    def test_rejecting_attributes(self):
        surround = Surround([HelloStage()])
        data = BasicData()
        surround.process(data)
        self.assertRaises(AttributeError, getattr, data, "no_text")

    def test_surround_config(self):
        path = os.path.dirname(__file__)
        config = Config()
        config.read_config_files([os.path.join(path, "config.yaml")])
        surround = Surround([HelloStage()], config)
        data = BasicData()
        surround.process(data)
        self.assertEqual(data.config_value, "Scott")

    def test_surround_override(self):
        path = os.path.dirname(__file__)
        surround = Surround([FirstStage()])
        config = Config()
        config.read_config_files([os.path.join(path, "stages.yaml")])
        surround.set_config(config)
        data = BasicData()
        surround.process(data)
        self.assertEqual(data.stage1, "first stage")
        self.assertEqual(data.stage2, "second stage")
