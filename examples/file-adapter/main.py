import logging
import os
import csv

from surround import Estimator, SurroundData, Assembler, Validator, Loader, Config

prefix = ""

class CSVLoader(Loader):
    def load(self, surround_data, config):
        input_path = prefix + config.get_path("Surround.Loader.input")
        with open(input_path) as csv_file:
            content = csv.DictReader(csv_file, delimiter=',', quotechar='"')
            # pylint: disable=unused-variable
            for i, row in enumerate(content):
                surround_data.inputs.append(row)

    def execute(self, surround_data, config, run_pipeline):
        for row in surround_data.inputs:
            surround_data.active_row = row
            run_pipeline()

        self.save_result(surround_data, config)

    def save_result(self, surround_data, config):
        output_path = prefix + config.get_path("Surround.Loader.output")
        with open(output_path, "w") as output_file:
            for a, b in surround_data.outputs:
                if b is None:
                    output_file.write("%d\n" % a)
                else:
                    output_file.write("%d,\"%s\"\n" % (a, b))
        logging.info("File written to %s", output_path)


class CSVValidator(Validator):
    def validate(self, surround_data, config):
        if not surround_data.inputs:
            raise ValueError("Input is empty")


class ProcessCSV(Estimator):
    def estimate(self, surround_data, config):
        surround_data.word_count = len(surround_data.active_row['Consumer complaint narrative'].split())

        if config and config.get_path("ProcessCSV.include_company"):
            surround_data.company = surround_data.active_row['Company']

        surround_data.outputs.append((surround_data.word_count, surround_data.company))

    def fit(self, surround_data, config):
        print("No training implemented")


class BasicData(SurroundData):
    inputs = []
    outputs = []
    row = None
    word_count = None
    company = None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    dir_extension = os.path.dirname(__file__)
    if dir_extension not in os.getcwd():
        prefix = dir_extension + "/"

    app_config = Config()
    app_config.read_config_files([prefix + "config.yaml"])
    assembler = Assembler("Loader example", BasicData(), ProcessCSV(), app_config)
    assembler.set_loader(CSVLoader(), CSVValidator())
    assembler.run()
