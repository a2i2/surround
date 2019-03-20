import json
from surround import Surround, Wrapper, AllowedTypes
from stages import CarData, EncodeImage, DetectCar, ExtractCar

class PipelineWrapper(Wrapper):
    def __init__(self):
        surround = Surround([EncodeImage(), DetectCar(), ExtractCar()], __name__)
        type_of_uploaded_object = AllowedTypes.IMAGE
        self.config = surround.config
        super().__init__(surround, type_of_uploaded_object)

    def run(self, input_data):
        data = CarData(input_data)
        self.surround.process(data)

        with open(("output/response.json"), 'w') as f:
            json.dump(data.output_data, f)
