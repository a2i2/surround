import logging
import abc
from surround import Stage, Pipeline
from web_service_runner import WebServiceRunner

# Python 2.7 and 3.5 compatible classes:
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})

class ParseData(Stage):
    def operate(self, pipeline_data, config):
        pipeline_data.output = {"result": "Hi, " + pipeline_data.input['name']}

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
