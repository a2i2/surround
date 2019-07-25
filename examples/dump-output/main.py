import logging
import os
from surround import Validator, Filter, Estimator, State, Assembler, Config

hello_file_path = "/stages/WriteHello/Output.txt"
world_file_path = "/stages/WriteWorld/Output.txt"

class WriteHello(Filter):
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def dump_output(self, state, config):
        text_file = open(self.dir_path + hello_file_path, "w")
        text_file.write(state.text)
        text_file.close()

    def operate(self, state, config):
        state.text = "Hello"


class WriteWorld(Estimator):
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def dump_output(self, state, config):
        text_file = open(self.dir_path + world_file_path, "w")
        text_file.write(state.text)
        text_file.close()

    def estimate(self, state, config):
        state.text = "World"

    def fit(self, state, config):
        print("Not training implementation")


class BasicData(State):
    text = None


class ValidateData(Validator):
    def validate(self, state, config):
        if state.text:
            raise ValueError("'text' is not None")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    path = os.path.dirname(os.path.realpath(__file__))

    app_config = Config()
    app_config.read_config_files([path + "/config.yaml"])
    assembler = Assembler("Dump output example", ValidateData())
    assembler.set_config(app_config)
    assembler.set_estimator(WriteWorld(path), [WriteHello(path)])
    assembler.run(BasicData())

    print("Hello output.txt contains '%s'" % open(path + hello_file_path, "r").read())
    print("World output.txt contains '%s'" % open(path + world_file_path, "r").read())
