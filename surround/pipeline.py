# pipeline.py
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

class PipelineData(Frozen):
    """
    Stores the data to be passed between each stage of a pipeline.
    Note that different stages of the pipeline are responsible for
    setting the attributes.
    """
    stage_metadata = []
    execution_time = None
    error = None
    warnings = []

class Pipeline(ABC):

    def __init__(self, pipeline_stages, config=None):
        assert isinstance(pipeline_stages, list), \
               "pipeline_stages must be a list of Stage objects"

        self.pipeline_stages = pipeline_stages
        self.config = None
        if config:
            self.set_config(config)

    def set_config(self, config):
        if not config or not isinstance(config, Config):
            raise TypeError("config should be of class Config")
        self.config = config
        if self.config["surround"]["stages"]:
            self.pipeline_stages = []
            result = self.config.get_path(self.config["surround"]["stages"])
            if not isinstance(result, list):
                result = [result]
            for stage in filter(None, result):
                parts = stage.split(".")
                module = import_module("." + parts[-2], ".".join(parts[:-2]))
                klass = getattr(module, parts[-1])
                self.pipeline_stages.append(klass())
        return True

    def _execute_stage(self, stage, stage_data):
        stage_start = datetime.now()
        stage.operate(stage_data, self.config)

        # Calculate and log stage duration
        stage_execution_time = datetime.now() - stage_start
        stage_data.stage_metadata.append({type(stage).__name__: str(stage_execution_time)})
        LOGGER.info("Stage %s took %s secs", type(stage).__name__, stage_execution_time)

    def process(self, pipeline_data):
        assert isinstance(pipeline_data, PipelineData), \
            "Input must be a PipelineData object or inherit from PipelineData"

        pipeline_data.freeze()
        pipeline_start = datetime.now()
        error = None
        try:
            for stage in self.pipeline_stages:
                assert isinstance(stage, Stage), \
                    "A stage must be an instance of the Stage class"
                self._execute_stage(stage, pipeline_data)
                if pipeline_data.error:
                    break

            pipeline_execution_time = datetime.now() - pipeline_start
            pipeline_data.execution_time = str(pipeline_execution_time)
            LOGGER.info("Pipeline took %s secs", pipeline_execution_time)

        except Exception:
            if error is None:
                error = "FAILED"
                LOGGER.exception("Failed processing pipeline")
                pipeline_data.thaw()
        return pipeline_data
