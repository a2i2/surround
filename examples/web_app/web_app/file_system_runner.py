"""
This module is responsible for loading the data and running the pipeline.
"""

import logging
from surround import Runner, RunMode
from .stages import AssemblerState

logging.basicConfig(level=logging.INFO)


class FileSystemRunner(Runner):
    def load_data(self, mode, config):
        raw_data = "Prepare data here"
        if mode == RunMode.BATCH_PREDICT:
            logging.info("No batch processing present")
        elif mode == RunMode.TRAIN:
            logging.info("No training pipeline present")
        else:
            logging.info("No prediction pipeline")
        return AssemblerState(raw_data)
