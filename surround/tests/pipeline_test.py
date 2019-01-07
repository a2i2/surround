import unittest
import os
from surround import Pipeline, Stage, PipelineData, Config
from .stages.first_stage import FirstStage

class HelloStage(Stage):
    def operate(self, data, config):
        data.text = "hello"
        if config:
            data.config_value = config["helloStage"]["suffix"]


class FailStage(Stage):
    def operate(self, data):
        data.no_text = "hello"


class BasicData(PipelineData):
    text = None
    config_value = None
    stage = None

class TestPipeline(unittest.TestCase):

    def test_happy_path(self):
        pipeline = Pipeline([HelloStage()])
        output = pipeline.process(BasicData())
        self.assertEqual(output.text, "hello")

    def test_rejecting_attributes(self):
        pipeline = Pipeline([HelloStage()])
        output = pipeline.process(BasicData())
        self.assertRaises(AttributeError, getattr, output, "no_text")

    def test_pipeline_config(self):
        path = os.path.dirname(__file__)
        config = Config()
        config.read_config_files([os.path.join(os.path.dirname(__file__), "config.yaml")])
        pipeline = Pipeline([HelloStage()], config)
        output = pipeline.process(BasicData())
        self.assertEqual(output.config_value, "Scott")

    def test_pipeline_override(self):
        path = os.path.dirname(__file__)
        pipeline = Pipeline([FirstStage()])
        config = Config()
        config.read_config_files([os.path.join(os.path.dirname(__file__), "stages.yaml")])
        pipeline.set_config(config)
        output = pipeline.process(BasicData())
        self.assertEqual(output.stage, "second stage")
