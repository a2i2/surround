from surround import Stage, PipelineData, Pipeline
import logging

class HelloStage(Stage):
    def operate(self, data):
        data.text = "hello"

class BasicData(PipelineData):
    text = None

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    pipeline = Pipeline([HelloStage()])
    output = pipeline.process(BasicData())
    print(output.text)
