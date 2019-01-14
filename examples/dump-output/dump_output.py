import logging
import os
from surround import Stage, SurroundData, Surround
from file_system_runner import FileSystemRunner

class WriteHello(Stage):
    def dump_output(self, output, config):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        text_file = open(dir_path + "/stages/WriteHello/Output.txt", "w")
        text_file.write(output.text)
        text_file.close()

    def operate(self, surround_data, config):
        surround_data.text = "Hello"

class WriteWorld(Stage):
    def dump_output(self, output, config):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        text_file = open(dir_path + "/stages/WriteWorld/Output.txt", "w")
        text_file.write(output.text)
        text_file.close()

    def operate(self, surround_data, config):
        surround_data.text = "World"

class BasicData(SurroundData):
    text = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    surround = Surround([WriteHello(), WriteWorld()])
    adapter = FileSystemRunner(surround,
                               description="A sample project to show dump intermediate ouput",
                               config_file="Path to configuration file")
    adapter.start()
    surround.process(BasicData())
