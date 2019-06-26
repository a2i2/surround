import logging
import os
import csv

from typing import List, Tuple
from surround import Estimator, SurroundData, Assembler, Validator, Config, Runner

prefix = ""


class BasicData(SurroundData):
    outputs: List[Tuple[int, str]] = []
    row: int = None
    word_count: int = None
    company: str = None


class MainRunner(Runner):
    def run(self, is_training: bool = False) -> None:
        self.assembler.init_assembler()
        data = BasicData()
        input_path = prefix + self.assembler.config.get_path("Surround.Loader.input")

        with open(input_path) as csv_file:
            content = csv.DictReader(csv_file, delimiter=',', quotechar='"')
            # pylint: disable=unused-variable
            for i, row in enumerate(content):
                data.active_row = row
                self.assembler.run(data)

        self.save_result(data, self.assembler.config)

    def save_result(self, surround_data: BasicData, config: Config) -> None:
        output_path = prefix + config.get_path("Surround.Loader.output")
        with open(output_path, "w") as output_file:
            for a, b in surround_data.outputs:
                if b is None:
                    output_file.write("%d\n" % a)
                else:
                    output_file.write("%d,\"%s\"\n" % (a, b))
        logging.info("File written to %s", output_path)


class CSVValidator(Validator):
    def validate(self, surround_data: BasicData, config: Config) -> None:
        if not surround_data.active_row:
            raise ValueError("'active_row' is empty")


class ProcessCSV(Estimator):
    def estimate(self, surround_data: BasicData, config: Config) -> None:
        surround_data.word_count = len(surround_data.active_row['Consumer complaint narrative'].split())

        if config and config.get_path("ProcessCSV.include_company"):
            surround_data.company = surround_data.active_row['Company']

        surround_data.outputs.append((surround_data.word_count, surround_data.company))

    def fit(self, surround_data: BasicData, config: Config) -> None:
        print("No training implemented")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    dir_extension = os.path.dirname(__file__)
    if dir_extension not in os.getcwd():
        prefix = dir_extension + "/"

    app_config = Config()
    app_config.read_config_files([prefix + "config.yaml"])
    assembler = Assembler("Loader example", CSVValidator(), ProcessCSV(), app_config)
    MainRunner(assembler).run()
