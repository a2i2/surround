from surround import Stage, SurroundData

class HelloStage(Stage):
    def operate(self, surround_data, config):
        surround_data.text = "hello"

class BasicData(SurroundData):
    text = None

    def __init__(self, input_data):
        self.input_data = input_data

class RotateImage(Stage):
    def operate(self, surround_data, config):
        """Add operate code
        """
