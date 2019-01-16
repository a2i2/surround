from abc import ABC, abstractmethod
import logging
from datetime import datetime

LOGGER = logging.getLogger(__name__)

class Stage(ABC):

    @abstractmethod
    def operate(self, surround_data, config):
        """
        A stage in a surround.
        :param surround_data: Instance or child of the SurroundData class.
                              Stores intermediate data from each stage in Surround.
        :param config: A ConfigParser object that contains the settings for each stage.
        """

    def log_duration(self, start_time, stage_data):
        # Calculate and log stage duration
        stage_execution_time = datetime.now() - start_time
        stage_data.stage_metadata.append({type(self).__name__: str(stage_execution_time)})
        LOGGER.info("Stage %s took %s secs", type(self).__name__, stage_execution_time)
