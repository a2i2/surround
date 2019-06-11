import unittest
import os
from surround import Assembler, Estimator, SurroundData, Config, Validator


test_text = "hello"


class HelloStage(Estimator):
    def estimate(self, surround_data, config):
        surround_data.text = test_text
        if "helloStage" in config:
            surround_data.config_value = config["helloStage"]["suffix"]

    def fit(self, surround_data, config):
        print("No training implemented")


class BasicData(SurroundData):
    text = None
    config_value = None
    stage1 = None
    stage2 = None


class ValidateData(Validator):
    def validate(self, surround_data, config):
        if surround_data.text:
            raise ValueError("'text' is not None")

        if surround_data.config_value:
            raise ValueError("'config_value' is not None")

        if surround_data.stage1:
            raise ValueError("'stage1' is not None")

        if surround_data.stage2:
            raise ValueError("'stage2' is not None")


class TestSurround(unittest.TestCase):

    def test_happy_path(self):
        data = BasicData()
        assembler = Assembler("Happy path", ValidateData(), HelloStage(), Config())
        assembler.init_assembler()
        assembler.run(data)
        self.assertEqual(data.text, test_text)

    def test_rejecting_attributes(self):
        data = BasicData()
        assembler = Assembler("Reject attribute", ValidateData(), HelloStage(), Config())
        assembler.init_assembler()
        assembler.run(data)
        self.assertRaises(AttributeError, getattr, data, "no_text")

    def test_surround_config(self):
        path = os.path.dirname(__file__)
        config = Config()
        config.read_config_files([os.path.join(path, "config.yaml")])
        data = BasicData()
        assembler = Assembler("Surround config", ValidateData(), HelloStage(), config)
        assembler.run(data)
        self.assertEqual(data.config_value, "Scott")
