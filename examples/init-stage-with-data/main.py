import logging
from surround import Stage, SurroundData, Surround

class HelloSurround(Stage):
    def __init__(self, data):
        self.data = data

    def operate(self, surround_data, config):
        surround_data.text = self.data
        print(surround_data.text)

class HelloWorld(Stage):
    def __init__(self, data):
        self.data = data

    def operate(self, surround_data, config):
        surround_data.text = self.data
        print(surround_data.text)

class BasicData(SurroundData):
    text = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    surround = Surround([HelloSurround("HelloSurround"), HelloWorld("HelloWorld")])
    surround.process(BasicData())
