# pipeline.py
#
# Manages a set of stages and the data that is passed between them.

import logging
from .stage import Stage
from datetime import datetime
import abc

# Python 2.7 and 3.5 compatible classes:
ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})

LOGGER = logging.getLogger(__name__)

class Frozen(object):
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

    def __init__(self, pipeline_stages):
        assert isinstance(pipeline_stages, list), \
               "pipeline_stages must be a list of Stage objects"
        self.pipeline_stages = pipeline_stages

    def _execute_stage(self, stage, stage_data):
        stage_start = datetime.now()
        stage.operate(stage_data)

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
