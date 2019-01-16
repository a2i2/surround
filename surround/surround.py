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
        self.data = None
        self.config = None
        if config:
            self.set_config(config)

    def _log_duration(self, start_time):
        # Calculate and log stage duration
        execution_time = datetime.now() - start_time
        self.data.execution_time = str(execution_time)
        LOGGER.info("Surround took %s secs", execution_time)

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

    def _execute_stage(self, stage):
        stage_start = datetime.now()
        stage.operate(self.data, self.config)
        stage.log_duration(stage_start, self.data)

    def process(self, data):
        self.data = data
        assert isinstance(self.data, SurroundData), \
            "Input must be a SurroundData object or inherit from SurroundData"

        self.data.freeze()
        start_time = datetime.now()
        error = None
        try:
            for stage in self.surround_stages:
                assert isinstance(stage, Stage), \
                    "A stage must be an instance of the Stage class"
                self._execute_stage(stage)
                if self.data.error:
                    break

            self._log_duration(start_time)

        except Exception:
            if error is None:
                error = "FAILED"
                LOGGER.exception("Failed processing Surround")
                self.data.thaw()
        return self.data
