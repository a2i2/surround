from surround import Stage, SurroundData
from surround.runner.wrapper import Wrapper
from surround import Surround

class HelloStage(Stage):
    def operate(self, surround_data, config):
        surround_data.text = "hello"

class BasicData(SurroundData):
    text = None

    def __init__(self, uploaded_data):
        self.uploaded_data = uploaded_data

class RotateImage(Stage):
    def operate(self, surround_data, config):
        print(surround_data.uploaded_data)

class PipelineWrapper(Wrapper):
    def __init__(self):
        surround = Surround([HelloStage(), RotateImage()])
        type_of_uploaded_object = "image"
        self.config = surround.config
        super().__init__(surround, type_of_uploaded_object)

    def run(self, uploaded_data):
        if super().run(uploaded_data):
            data = BasicData(uploaded_data)
            self.surround.process(data)
            print(data.text)
