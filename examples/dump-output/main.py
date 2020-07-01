import logging
import os
from surround import Stage, Estimator, State, Assembler, Config

hello_file_path = "/stages/WriteHello/Output.txt"
world_file_path = "/stages/WriteWorld/Output.txt"

class WriteHello(Stage):
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def dump_output(self, state, config):
        with open(self.dir_path + hello_file_path, "w") as text_file:
            text_file.write(state.text)

    def operate(self, state, config):
        state.text = "Hello"


class WriteWorld(Estimator):
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def dump_output(self, state, config):
        with open(self.dir_path + world_file_path, "w") as text_file:
            text_file.write(state.text)


    def estimate(self, state, config):
        state.text = "World"

    def fit(self, state, config):
        print("Not training implementation")


class AssemblerState(State):
    text = None


class InputValidator(Stage):
    def operate(self, state, config):
        if state.text:
            raise ValueError("'text' is not None")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    path = os.path.dirname(os.path.realpath(__file__))

    app_config = Config()
    app_config.read_config_files([path + "/config.yaml"])
    assembler = Assembler("Dump output example")
    assembler.set_stages([InputValidator(), WriteHello(path), WriteWorld(path)])
    assembler.set_config(app_config)
    assembler.run(AssemblerState())

    print("Hello output.txt contains '%s'" % open(path + hello_file_path, "r").read())
    print("World output.txt contains '%s'" % open(path + world_file_path, "r").read())
