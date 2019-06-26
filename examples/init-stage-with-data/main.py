import logging
import os

from typing import TextIO
from surround import Estimator, SurroundData, Assembler, Config, Validator

prefix = ""


class BasicData(SurroundData):
    text: str = None


class HelloWorld(Estimator):
    def __init__(self) -> None:
        self.file_: TextIO = None

    def init_stage(self, config: Config) -> None:
        filename = config.get_path("surround.path_to_HelloWorld")
        self.file_ = open(prefix + filename, "r")

    def estimate(self, surround_data: BasicData, config: Config) -> None:
        surround_data.text = self.file_.read()

    def fit(self, surround_data: BasicData, config: Config) -> None:
        print("No training implemented")


class ValidateData(Validator):
    def validate(self, surround_data: BasicData, config: Config) -> None:
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
