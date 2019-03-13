from surround import Stage, SurroundData
from surround.runner.wrapper import Wrapper
from surround import Surround

class HelloStage(Stage):
    def operate(self, surround_data, config):
        surround_data.text = "hello"

class BasicData(SurroundData):
    text = None

class WebWrapper(Wrapper):
    def __init__(self):
        surround = Surround([HelloStage()])
        self.config = surround.config
        super().__init__(surround)

    def run(self):
        data = BasicData()
        self.surround.process(data)
        print(data.text)
