import logging
from surround import Stage, SurroundData, Surround

class HelloStage(Stage):
    def operate(self, surround_data, config=None):
        surround_data.text = "hello"

class BasicData(SurroundData):
    text = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    surround = Surround([HelloStage()])
    output = surround.process(BasicData())
    print(output.text)
