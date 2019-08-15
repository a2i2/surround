import logging
import os
import csv

from surround import Estimator, State, Assembler, Validator, Config, Runner

prefix = ""

class MainRunner(Runner):
    def run(self, is_training=False):
        self.assembler.init_assembler()
        data = AssemblerState()
        input_path = prefix + self.assembler.config.get_path("Surround.Loader.input")

        with open(input_path) as csv_file:
            content = csv.DictReader(csv_file, delimiter=',', quotechar='"')
            # pylint: disable=unused-variable
            for i, row in enumerate(content):
                data.active_row = row
                self.assembler.run(data)

        self.save_result(data, self.assembler.config)

    def save_result(self, state, config):
        output_path = prefix + config.get_path("Surround.Loader.output")
        with open(output_path, "w") as output_file:
            for a, b in state.outputs:
                if b is None:
                    output_file.write("%d\n" % a)
                else:
                    output_file.write("%d,\"%s\"\n" % (a, b))
        logging.info("File written to %s", output_path)


class CSVValidator(Validator):
    def validate(self, state, config):
        if not state.active_row:
            raise ValueError("'active_row' is empty")


class ProcessCSV(Estimator):
    def estimate(self, state, config):
        state.word_count = len(state.active_row['Consumer complaint narrative'].split())

        if config and config.get_path("ProcessCSV.include_company"):
            state.company = state.active_row['Company']

        state.outputs.append((state.word_count, state.company))

    def fit(self, state, config):
        print("No training implemented")


class AssemblerState(State):
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
