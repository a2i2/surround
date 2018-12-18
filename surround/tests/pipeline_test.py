import unittest
from surround import Pipeline, Stage, PipelineData
import sys
import io
import os

PY3 = sys.version_info[0] == 3

if PY3:
    writer_file =  io.StringIO
else:
    writer_file =  io.BytesIO


class HelloStage(Stage):
    def operate(self, data, config):
        data.text = "hello"
        if config:
            data.config_value = config.get("HelloStage", "suffix")


class FailStage(Stage):
    def operate(self, data):
        data.no_text = "hello"

class BasicData(PipelineData):
    text = None
    config_value = None

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
        pipeline = Pipeline([HelloStage()], os.path.join(path, "config.cfg"))
        output = pipeline.process(BasicData())
        self.assertEqual(output.config_value, "Scott")
