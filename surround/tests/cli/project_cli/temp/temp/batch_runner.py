import logging
from surround import Runner
from stages import AssemblerState

logging.basicConfig(level=logging.INFO)

class BatchRunner(Runner):
    def run(self, is_training=False):
        self.assembler.init_assembler(True)
        data = AssemblerState()

        # Load data to be processed
        raw_data = "TODO: Load raw data here"

        # Setup input data
        data.input_data = raw_data

        # Run assembler
        self.assembler.run(data, is_training)

        logging.info("Batch Runner: %s", data.output_data)
