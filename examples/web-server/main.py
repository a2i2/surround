from surround import Stage, PipelineData, Pipeline
from web_service_runner import WebServiceRunner
import logging
import abc

# Python 2.7 and 3.5 compatible classes:
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})

class ParseData(Stage):
    def operate(self, data, config):
        data.output = { "result": "Hi, " + data.input['name'] }

def metadata():
    return {
        "input": {
            "name": {
                "type": "text"
            }
        }, "output": {
            "result": {
                "type": "text"
            }
        }, "version": "1.0.0"
    }

pipeline = Pipeline([ParseData()])
runner = WebServiceRunner(pipeline, metadata())
app = runner.app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=8000)
