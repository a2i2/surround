import os
from surround import Runner, RunMode
from .stages import AssemblyState


class BatchRunner(Runner):
    def load_data(self, mode, config):
        path = os.path.dirname(__file__) + "/data/input.txt"
        data = AssemblyState()

        with open(path, 'r') as f:
            data.lines = f.readlines()

        return data

    def run(self, mode=RunMode.BATCH_PREDICT):
        self.assembler.init_assembler(mode == RunMode.BATCH_PREDICT)

        data = self.load_data(mode, self.assembler.config)

        for line in data.lines:
            # Each line needs to be processed by the pipeline
            data.input_data = line.rstrip() + " "
            # Start assembler to process processed data
            self.assembler.run(data)

        print("Batch Runner: %s" % data.output_data)
