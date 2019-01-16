# surround.py
#
# Manages a set of stages and the data that is passed between them.
from importlib import import_module
import logging
from datetime import datetime
from abc import ABC
from .stage import Stage
from .config import Config

LOGGER = logging.getLogger(__name__)

class Frozen():
    """
    A class that can toggle the ability of adding new attributes.
    """
    __isfrozen = False
    def __setattr__(self, key, value):
        if self.__isfrozen and not hasattr(self, key):
            raise TypeError("%r is a frozen object" % self)
        object.__setattr__(self, key, value)

    def freeze(self):
        self.__isfrozen = True

    def thaw(self):
        self.__isfrozen = False

class SurroundData(Frozen):
    """
    Stores the data to be passed between each stage in Surround.
    Note that different stages inside Surround are responsible for
    setting the attributes.
    """
    stage_metadata = []
    execution_time = None
    error = None
    warnings = []

class Surround(ABC):

    def __init__(self, surround_stages, config=Config()):
        assert isinstance(surround_stages, list), \
               "surround_stages must be a list of Stage objects"

        self.surround_stages = surround_stages
        self.config = None
        if config:
            self.set_config(config)

    def set_config(self, config):
        if not config or not isinstance(config, Config):
            raise TypeError("config should be of class Config")
        self.config = config
        if self.config["surround"]["stages"]:
            self.surround_stages = []
            result = self.config.get_path(self.config["surround"]["stages"])
            if not isinstance(result, list):
                result = [result]
            for stage in filter(None, result):
                parts = stage.split(".")
                module = import_module("." + parts[-2], ".".join(parts[:-2]))
                klass = getattr(module, parts[-1])
                self.surround_stages.append(klass())
        return True

    def _execute_stage(self, stage, stage_data):
        stage_start = datetime.now()
        stage.operate(stage_data, self.config)

        if self.config["surround"]["enable_stage_output_dump"]:
            stage.dump_output(stage_data, self.config)

        # Calculate and log stage duration
        stage_execution_time = datetime.now() - stage_start
        stage_data.stage_metadata.append({type(stage).__name__: str(stage_execution_time)})
        LOGGER.info("Stage %s took %s secs", type(stage).__name__, stage_execution_time)

    def process(self, surround_data):
        assert isinstance(surround_data, SurroundData), \
            "Input must be a SurroundData object or inherit from SurroundData"

        surround_data.freeze()
        start_time = datetime.now()
        error = None
        try:
            for stage in self.surround_stages:
                assert isinstance(stage, Stage), \
                    "A stage must be an instance of the Stage class"
                self._execute_stage(stage, surround_data)
                if surround_data.error:
                    break

            execution_time = datetime.now() - start_time
            surround_data.execution_time = str(execution_time)
            LOGGER.info("Surround took %s secs", execution_time)

        except Exception:
            if error is None:
                error = "FAILED"
                LOGGER.exception("Failed processing Surround")
                surround_data.thaw()
        return surround_data
