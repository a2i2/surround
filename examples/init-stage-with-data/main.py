import logging
import os

from surround import Estimator, State, Assembler, Config, Validator

prefix = ""

class HelloWorld(Estimator):
    def __init__(self):
        self.file_ = None

    def initialise(self, config):
        filename = config.get_path("surround.path_to_HelloWorld")
        self.file_ = open(prefix + filename, "r")

    def estimate(self, state, config):
        state.text = self.file_.read()

    def fit(self, state, config):
        print("No training implemented")


class AssemblerState(State):
    text = None


class InputValidator(Validator):
    def validate(self, state, config):
        if state.text:
            raise ValueError("'text' is not None")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    dir_extension = os.path.dirname(__file__)
    if dir_extension not in os.getcwd():
        prefix = dir_extension + "/"

    app_config = Config()
    app_config.read_config_files([prefix + "config.yaml"])

    data = AssemblerState()
    assembler = Assembler("Init state example").set_validator(InputValidator()).set_estimator(HelloWorld()).set_config(app_config)
    assembler.init_assembler()
    assembler.run(data)

    print("Text is '%s'" % data.text)
