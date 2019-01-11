import logging
import abc
from surround import Stage, Surround
from web_service_runner import WebServiceRunner

# Python 2.7 and 3.5 compatible classes:
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})

class ParseData(Stage):
    def operate(self, surround_data, config=None):
        surround_data.output = {"result": "Hi, " + surround_data.input['name']}

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

surround = Surround([ParseData()])
runner = WebServiceRunner(surround, metadata())
app = runner.app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=8000)
