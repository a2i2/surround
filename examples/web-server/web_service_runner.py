from surround import PipelineData
from flask import Flask, jsonify, request
import abc
import sys
import logging

# Python 2.7 and 3.5 compatible classes:
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})

LOGGER = logging.getLogger(__name__)

class TestData(PipelineData):
    input = None
    output = None

class MetadataAction(object):
    def __init__(self, metadata):
        self.metadata = metadata

    def __call__(self, *args):
        return jsonify(self.metadata)

class PredictAction(object):
    methods = ['POST']

    def __init__(self, pipeline, metadata):
        self.metadata = metadata
        self.pipeline = pipeline

    def __call__(self, *args):
        response = {}
        if (request.is_json):
            data = TestData()
            data.input = request.get_json()
            self.pipeline.process(data)
            response = {
                "output": data.output,
                "version": self.metadata['version']
            }
        else:
            data.input = request.json
            response = {
                "error": "Input is not a valid JSON"
            }

        return jsonify(response)

class WebServiceRunner(ABC):
    app = None

    def __init__(self, pipeline, metadata=None):
        self.app = Flask(__name__)

        assert (metadata != None), "Metada is required"
        try:
            metadata['input']
        except KeyError:
            LOGGER.info('AssertionError: Missing "input" information in metadata')
            sys.exit(1)
        try:
            metadata['output']
        except KeyError:
            LOGGER.info('AssertionError: Missing "output" information in metadata')
            sys.exit(1)
        try:
            metadata['version']
        except KeyError:
            LOGGER.info('AssertionError: Missing "version" information in metadata')
            sys.exit(1)

        self.app.add_url_rule('/metadata', 'metadata', MetadataAction(metadata))
        self.app.add_url_rule('/predict', 'predict', PredictAction(pipeline, metadata))

    def start(self):
        self.app.run(host='0.0.0.0', debug=True)
