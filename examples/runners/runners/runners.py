import os
from surround import Runner
from .stages import RunnersData


class BatchRunner(Runner):
    def prepare_runner(self):
        path = os.path.dirname(__file__)
        self.path = path + "/data/input.txt"
        self.data = RunnersData()

    def prepare_data(self):
        self.data.input_data = self.raw_data.rstrip() + " "

    def run(self):
        self.prepare_runner()
        self.assembler.init_assembler()
        with open(self.path, 'r') as f:
            for line in f:
                # Each line needs to be processed by the pipeline
                self.raw_data = line
                self.prepare_data()
                # Start assembler to process processed data
                self.assembler.run(self.data)

        print("Batch Runner: %s" % self.data.output_data)
