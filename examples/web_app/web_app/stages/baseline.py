"""
This module defines the baseline estimator in the pipeline.
"""

import logging
from surround import Estimator
import mlflow

LOGGER = logging.getLogger(__name__)


class Baseline(Estimator):
    def estimate(self, state, config):
        state.output_data = state.input_data
        with mlflow.start_run():
            mlflow.log_dict(config._storage, "config.yaml")

    def fit(self, state, config):
        LOGGER.info("TODO: Train your model here")
