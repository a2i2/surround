import logging
import os
import csv

from surround import Estimator, SurroundData, Assembler, Validator, Config, Runner

prefix = ""

class MainRunner(Runner):
    def prepare_runner(self):
        self.input_path = prefix + self.assembler.config.get_path("Surround.Loader.input")
        self.data = BasicData()

    def prepare_data(self):
        with open(self.input_path) as csv_file:
            content = csv.DictReader(csv_file, delimiter=',', quotechar='"')
            # pylint: disable=unused-variable
            for i, row in enumerate(content):
                self.data.inputs.append(row)

    def run(self, is_training=False):
        self.prepare_runner()
        self.assembler.init_assembler(self.data)
        self.prepare_data()

        for row in self.data.inputs:
            self.data.active_row = row

            # Start assembler to process processed data
            self.assembler.run()

        self.save_result(self.data, self.assembler.config)

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
    assembler = Assembler("Loader example", CSVValidator(), ProcessCSV(), app_config)
    MainRunner(assembler).run()
