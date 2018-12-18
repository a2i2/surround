import unittest
from surround import Pipeline, Stage, PipelineData


class HelloStage(Stage):
    def operate(self, data):
        data.text = "hello"

class FailStage(Stage):
    def operate(self, data):
        data.no_text = "hello"


class BasicData(PipelineData):
    text = None

class TestPipeline(unittest.TestCase):

    def test_happy_path(self):
        pipeline = Pipeline([HelloStage()])
        output = pipeline.process(BasicData())
        self.assertEqual(output.text, "hello")

    def test_rejecting_attributes(self):
        pipeline = Pipeline([HelloStage()])
        output = pipeline.process(BasicData())
        self.assertRaises(AttributeError, getattr, output, "no_text")
