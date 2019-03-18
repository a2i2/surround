from surround import Stage, SurroundData

class HelloStage(Stage):
    def operate(self, surround_data, config):
        surround_data.text = "hello"

class BasicData(SurroundData):
    text = None

    def __init__(self, uploaded_data):
        self.uploaded_data = uploaded_data

class RotateImage(Stage):
    def operate(self, surround_data, config):
        """Add operate code
        """
