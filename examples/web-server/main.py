from surround import Stage, PipelineData, Pipeline, WebServiceRunner
import logging

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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    pipeline = Pipeline([ParseData()])
    runner = WebServiceRunner(pipeline, metadata())
    runner.start()
