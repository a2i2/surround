import logging
from surround import Stage, PipelineData, Pipeline

class HelloStage(Stage):
    def operate(self, pipeline_data, config):
        pipeline_data.text = "hello"

class BasicData(PipelineData):
    text = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = Pipeline([HelloStage()])
    output = pipeline.process(BasicData())
    print(output.text)
