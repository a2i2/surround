import logging
import os
import csv

from surround import Estimator, State, Assembler, Stage, Runner, RunMode, load_config
from config import Config

prefix = ""


class MainRunner(Runner):
    def load_data(self, mode, config):
        state = AssemblerState()
        input_path = prefix + config.loader.input

        with open(input_path) as csv_file:
            state.rows = list(csv.DictReader(csv_file, delimiter=",", quotechar='"'))

        return state

    def run(self, mode=RunMode.BATCH_PREDICT):
        super().run(mode)
        self.save_result(self.assembler.state, self.assembler.config)

    def save_result(self, state, config):
        output_path = prefix + config.loader.output
        with open(output_path, "w") as output_file:
            for a, b in state.outputs:
                if b is None:
                    output_file.write("%d\n" % a)
                else:
                    output_file.write('%d,"%s"\n' % (a, b))
        logging.info("File written to %s", output_path)


class CSVValidator(Stage):
    def operate(self, state, config):
        if not state.rows:
            raise ValueError("'rows' is empty")


class ProcessCSV(Estimator):
    def estimate(self, state, config):
        for row in state.rows:
            state.word_count = len(row["Consumer complaint narrative"].split())

            if config and config.process_csv.include_company:
                state.company = row["Company"]

            state.outputs.append((state.word_count, state.company))

    def fit(self, state, config):
        print("No training implemented")


class AssemblerState(State):
    outputs = []
    rows = []
    row = None
    word_count = None
    company = None
    csv_file = None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    dir_extension = os.path.dirname(__file__)
    if dir_extension not in os.getcwd():
        prefix = dir_extension + "/"

    app_config = load_config(name="config", config_class=Config)
    assembler = (
        Assembler("Loader example")
        .set_stages([CSVValidator(), ProcessCSV()])
        .set_config(app_config)
    )

    MainRunner(assembler).run()
