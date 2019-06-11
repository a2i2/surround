import os
from surround import Runner
from .stages import RunnersData


class BatchRunner(Runner):

    def run(self, is_training=False):
        self.assembler.init_assembler(True)

        path = os.path.dirname(__file__) + "/data/input.txt"
        data = RunnersData()

        with open(path, 'r') as f:
            for line in f:
                # Each line needs to be processed by the pipeline
                data.input_data = line.rstrip() + " "
                # Start assembler to process processed data
                self.assembler.run(data)

        print("Batch Runner: %s" % data.output_data)
