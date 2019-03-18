from surround import Surround, Wrapper, AllowedTypes
from stages import HelloStage, RotateImage, BasicData

class PipelineWrapper(Wrapper):
    def __init__(self):
        surround = Surround([HelloStage(), RotateImage()])
        type_of_uploaded_object = AllowedTypes.IMAGE
        self.config = surround.config
        super().__init__(surround, type_of_uploaded_object)

    def run(self, uploaded_data):
        data = BasicData(uploaded_data)
        self.surround.process(data)
