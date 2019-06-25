import logging
import os

from surround import Estimator, SurroundData, Assembler, Config, Validator

prefix = ""

class HelloWorld(Estimator):
    def __init__(self):
        self.file_ = None

    def initialise(self, config):
        filename = config.get_path("surround.path_to_HelloWorld")
        self.file_ = open(prefix + filename, "r")

    def estimate(self, surround_data, config):
        surround_data.text = self.file_.read()

    def fit(self, surround_data, config):
        print("No training implemented")


class BasicData(SurroundData):
    text = None


class ValidateData(Validator):
    def validate(self, surround_data, config):
        if surround_data.text:
            raise ValueError("'text' is not None")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    dir_extension = os.path.dirname(__file__)
    if dir_extension not in os.getcwd():
        prefix = dir_extension + "/"

    app_config = Config()
    app_config.read_config_files([prefix + "config.yaml"])

    data = BasicData()
    assembler = Assembler("Init state example", ValidateData(), HelloWorld(), app_config)
    assembler.init_assembler()
    assembler.run(data)

    print("Text is '%s'" % data.text)
