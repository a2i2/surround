# assembler.py

import logging
import os
import sys
from abc import ABC
from datetime import datetime

from .config import BaseConfig
from .run_modes import RunMode
from .stage import Stage, Estimator

LOGGER = logging.getLogger(__name__)


class Assembler(ABC):
    """
    Class responsible for assembling and executing a Surround pipeline.

    Responsibilities:

    - Encapsulate the configuration data and pipeline stages
    - Load configuration from a specified module
    - Run the pipeline with input data in predict/batch/train mode

    For more information on this process, see the :ref:`about` page.

    Example::

        assembler = Assembler("Example pipeline")
        assembler.set_stages([PreFilter(), PredictStage(), PostFilter()])
        assembler.init_assembler(batch_mode=False)

        data = AssemblyState("some data")
        assembler.run(data, is_training=False)

    Batch-predict mode::

        assembler.init_assembler(batch_mode=True)
        assembler.run(data, is_training=False)

    Training mode::

        assembler.init_assembler(batch_mode=True)
        assembler.run(data, is_training=True)

    Predict/Estimate mode::

        assembler.init_assembler(batch_mode=False)
        assembler.run(data, is_training=False)
        
    Constructor for an Assembler pipeline:

    :param assembler_name: The name of the pipeline
    :type assembler_name: str
    :param config: Configuration instance
    :type config: BaseConfig
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, assembler_name="", config=BaseConfig()):
        self.assembler_name = assembler_name
        self.config = config
        self.stages = None
        self.batch_mode = False
        self.finaliser = None
        self.state = None
        self.metrics = None

    def init_assembler(self):

        """
        Initializes the assembler and all of it's stages.

        Calls the :meth:`surround.stage.Stage.initialise` method of all stages and the estimator.

        .. note:: Should be called after :meth:`surround.assembler.Assembler.set_config`.

        :returns: whether the initialisation was successful
        :rtype: bool
        """

        try:
            if self.stages:
                estimator_count = 0
                for stage in self.stages:
                    stage.initialise(self.config)
                    if isinstance(stage, Estimator):
                        estimator_count += 1
                    if estimator_count > 1:
                        raise ValueError("Stages can only have one Estimator class")

            if self.finaliser:
                self.finaliser.initialise(self.config)

        except Exception as e:
            if self.config.surround.surface_exceptions:
                raise e
            LOGGER.exception(e)
            return False
        return True

    def run(self, state=None, mode=RunMode.PREDICT):
        """
        Run the pipeline using the input data provided.

        If ``mode`` is set to ``RunMode.TRAIN`` then when it gets to the execution of the estimator,
        it will use the :meth:`surround.stage.Estimator.fit` method instead.

        If ``surround.enable_stage_output_dump`` is enabled in the Config instance then each stage and
        estimator's :meth:`surround.stage.Stage.dump_output` method will be called.

        This method doesn't return anything, instead results should be stored in the ``state``
        object passed in the parameters.

        :param state: Data passed between each stage in the pipeline
        :type state: :class:`surround.State`
        :param is_training: Run the pipeline in training mode or not
        :type is_training: bool
        """
        is_training = mode == RunMode.TRAIN

        LOGGER.info("Starting '%s'", self.assembler_name)

        if not self.stages:
            raise ValueError("There are no stages to run!")

        if not state:
            raise ValueError("state is required to run an assembler")
        self.state = state

        state.freeze()

        has_estimator = [s for s in self.stages if isinstance(s, Estimator)]
        if is_training and not has_estimator:
            raise ValueError("No Estimator class added to stages.")

        def _run_stage_safe(a_stage):
            start_time = datetime.now()
            try:
                if isinstance(a_stage, Estimator):
                    if is_training:
                        a_stage.fit(state, self.config)
                    else:
                        a_stage.estimate(state, self.config)
                else:
                    a_stage.operate(state, self.config)

                if self.config.surround.enable_stage_output_dump:
                    a_stage.dump_output(state, self.config)

            except Exception as e:
                if self.config.surround.surface_exceptions:
                    raise e
                state.errors.append(str(e))
                LOGGER.exception(e)
            execution_time = datetime.now() - start_time
            state.execution_time.append(str(execution_time))
            LOGGER.info("%s took %s secs", type(a_stage).__name__, execution_time)

        for stage in self.stages:
            _run_stage_safe(stage)
            if state.errors:
                break

        if self.metrics and mode != RunMode.PREDICT:
            _run_stage_safe(self.metrics)

        if self.finaliser:
            _run_stage_safe(self.finaliser)

        if state.errors:
            LOGGER.error(state.errors)

        state.thaw()

    def set_config(self, config):
        """
        Set the configuration data to be used during pipeline execution.

        .. note:: Should be called before :meth:`surround.assembler.Assembler.init_assembler`.

        :param config: the configuration data
        :type config: :class:`surround.config.BaseConfig`
        """

        self.config = config

        return self

    def set_stages(self, stages):
        """
        Set the stages to be executed one after the other in the pipeline.

        :param stages: list of stages to execute
        :type stages: list of :class:`surround.stage.Stage`
        """

        if not isinstance(stages, list) or not all([issubclass(type(x), Stage) for x in stages]):
            raise ValueError("stages must be a list of Stages's only!")

        self.stages = stages

        return self

    def set_finaliser(self, finaliser):
        """
        Set the final stage that will be executed no matter how the pipeline runs.
        This will be executed even when the pipeline fails or throws an error.

        :param finaliser: the final stage instance
        :type finaliser: :class:`surround.stage.Stage`
        """

        # finaliser must be a type of Stage
        if not finaliser and not isinstance(finaliser, Stage):
            raise TypeError("finaliser should be of class Stage")
        self.finaliser = finaliser

        return self

    def set_metrics(self, metrics):
        """
        When running batch or training jobs this stage is ran after all stages 
        but the finaliser stage. The purpose of this stage is to calculate metrics. 
        """

        if not metrics and not isinstance(metrics, Stage):
            raise TypeError("metrics should be of the Stage class")

        self.metrics = metrics

        return self
