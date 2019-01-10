import logging
import os
import csv
from surround import Stage, PipelineData, Pipeline, FileSystemAdapter

class CustomFileSystemAdapter(FileSystemAdapter):

    def transform(self, input_data):
        output = []
        with open(input_data.file0) as csv_file:
            content = csv.DictReader(csv_file, delimiter=',', quotechar='"')
            for i, row in enumerate(content):
                logging.info("Processing row %d", i)
                data = BasicData(row)
                self.pipeline.process(data)
                output.append((data.word_count, data.company))


        output_path = os.path.abspath(os.path.join(input_data.output_dir, "output.txt"))
        with open(output_path, "w") as output_file:
            for a, b in output:
                if b is None:
                    output_file.write("%d\n" % a)
                else:
                    output_file.write("%d,\"%s\"\n" % (a, b))
        logging.info("File written to %s", output_path)

class ProcessCSV(Stage):
    def operate(self, pipeline_data, config=None):
        pipeline_data.word_count = len(pipeline_data.row_dict['Consumer complaint narrative'].split())

        if config and config.get_path("ProcessCSV.include_company"):
            pipeline_data.company = pipeline_data.row_dict['Company']

class BasicData(PipelineData):
    word_count = None
    company = None

    def __init__(self, row_dict):
        self.row_dict = row_dict

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    pipeline = Pipeline([ProcessCSV()])
    adapter = CustomFileSystemAdapter(pipeline,
                                      description="A sample project to process a CSV file",
                                      output_dir="Directory to store the output",
                                      config_file="Path to configuration file",
                                      file0="Input CSV file")
    adapter.start()
