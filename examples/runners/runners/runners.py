import os
from surround import Runner

class SingleRunner(Runner):
    def prepare_runner(self):
        self.message = "Hello world"

    def prepare_data(self):
        self.assembler.surround_data.input_data = self.message

    def run(self):
        self.prepare_runner()
        self.prepare_data()
        # Start assembler to process processed data
        self.assembler.init_assembler()
        self.assembler.run()


class BatchRunner(Runner):
    def prepare_runner(self):
        path = os.path.dirname(__file__)
        self.file = open(path + "/data/input.txt")

    def prepare_data(self):
        self.assembler.surround_data.input_data = self.raw_data.rstrip() + " "

    def run(self):
        self.prepare_runner()
        for line in self.file:
            # Each line needs to be processed by the pipeline
            self.raw_data = line
            self.prepare_data()
            # Start assembler to process processed data
            self.assembler.init_assembler()
            self.assembler.run()
