import unittest
import os
from surround import Surround, Stage, SurroundData, Config
from .stages.first_stage import FirstStage

class HelloStage(Stage):
    def operate(self, surround_data, config):
        surround_data.text = "hello"
        if config:
            surround_data.config_value = config["helloStage"]["suffix"]

class BasicData(SurroundData):
    text = None
    config_value = None
    stage1 = None
    stage2 = None

class TestSurround(unittest.TestCase):

    def test_happy_path(self):
        surround = Surround([HelloStage()])
        output = surround.process(BasicData())
        self.assertEqual(output.text, "hello")

    def test_rejecting_attributes(self):
        surround = Surround([HelloStage()])
        output = surround.process(BasicData())
        self.assertRaises(AttributeError, getattr, output, "no_text")

    def test_surround_config(self):
        path = os.path.dirname(__file__)
        config = Config()
        config.read_config_files([os.path.join(path, "config.yaml")])
        surround = Surround([HelloStage()], config)
        output = surround.process(BasicData())
        self.assertEqual(output.config_value, "Scott")

    def test_surround_override(self):
        path = os.path.dirname(__file__)
        surround = Surround([FirstStage()])
        config = Config()
        config.read_config_files([os.path.join(path, "stages.yaml")])
        surround.set_config(config)
        output = surround.process(BasicData())
        self.assertEqual(output.stage1, "first stage")
        self.assertEqual(output.stage2, "second stage")
