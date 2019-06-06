import logging
import os

from surround import Estimator, SurroundData, Assembler, Config

prefix = ""

class HelloWorld(Estimator):

    def __init__(self):
        self.file_ = None

    def init_stage(self, config):
        filename = config.get_path("surround.path_to_HelloWorld")
        self.file_ = open(prefix + filename, "r")

    def estimate(self, surround_data, config):
        surround_data.text = self.file_.read()

    def fit(self, surround_data, config):
        print("No training implemented")


class BasicData(SurroundData):
    text = None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    dir_extension = os.path.dirname(__file__)
    if dir_extension not in os.getcwd():
        prefix = dir_extension + "/"

    app_config = Config()
    app_config.read_config_files([prefix + "config.yaml"])

    data = BasicData()
    assembler = Assembler("Init state example", data, HelloWorld(), app_config)
    assembler.init_assembler()
    assembler.run()

    print("Text is '%s'" % data.text)
