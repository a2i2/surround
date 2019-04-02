from surround import Surround, Wrapper, AllowedTypes
from stages import HelloStage, RotateImage, BasicData

class PipelineWrapper(Wrapper):
    def __init__(self):
        surround = Surround([HelloStage(), RotateImage()])
        type_of_uploaded_object = AllowedTypes.FILE
        self.config = surround.config
        super().__init__(surround, type_of_uploaded_object)

    def run(self, input_data):
        data = BasicData(input_data)
        self.surround.process(data)
