# assembler.py

import sys
import os
import logging

from abc import ABC
from datetime import datetime

from .config import Config, has_config
from .stage import Filter, Estimator, Validator
from .visualiser import Visualiser

LOGGER = logging.getLogger(__name__)

class Assembler(ABC):
    """
    Class responsible for assembling and executing a Surround pipeline.

    Responsibilties:

    - Encapsulate the configuration data, validator, filter(s), visualiser, and estimator.
    - Initialize all filters and the estimator
    - Load configuration from a specified module
    - Run the pipeline with input data in predict/batch/train mode

    Where running the pipeline involves passing the data to each stage in the following order:

    Validator -> Pre-filter(s) -> Estimator -> Post-filter(s) -> Visualiser

    For more information on this process, see the :ref:`about` page.

    Example::

        assembler = Assembler("Example pipeline")
        assembler.set_validator(Validation())
        assembler.set_estimator(PredictStage(), [PreFilter()], [PostFilter()])
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
    """

    # pylint: disable=too-many-instance-attributes
    @has_config
    def __init__(self, assembler_name="", config=None):
        """
        Constructor for an Assembler pipeline:

        :param assembler_name: The name of the pipeline
        :type assembler_name: str
        """

        self.assembler_name = assembler_name
        self.config = config
        self.stages = None
        self.estimator = None
        self.validator = None
        self.pre_filters = None
        self.post_filters = None
        self.visualiser = None
        self.batch_mode = False
        self.finaliser = None

    def init_assembler(self, batch_mode=False):
        """
        Initializes the assembler and all of it's stages.

        Calls the :meth:`surround.stage.Stage.initialise` method of all filters and the estimator.
        Also used set the variable ``batch_mode`` which is then used to determine if the visualiser
        should be used after all the stages have been executed.

        .. note:: Should be called after :meth:`surround.assembler.Assembler.set_estimator` and
                :meth:`surround.assembler.Assembler.set_config`.

        :param batch_mode: Whether batch mode should be used
        :type batch_mode: bool
        :returns: whether the initialisation was successful
        :rtype: bool
        """

        self.batch_mode = batch_mode
        try:
            if self.stages:
                for stage in self.stages:
                    stage.initialise(self.config)

            if self.validator:
                self.validator.initialise(self.config)

            if self.pre_filters:
                for pre_filter in self.pre_filters:
                    pre_filter.initialise(self.config)

            if self.estimator:
                self.estimator.initialise(self.config)

            if self.post_filters:
                for post_filter in self.post_filters:
                    post_filter.initialise(self.config)

            if self.finaliser:
                self.finaliser.initialise(self.config)

            if self.visualiser:
                self.visualiser.initialise(self.config)
        except Exception:
            LOGGER.exception("Failed initiating Assembler")
            return False

        return True

    def run(self, state=None, is_training=False):
        """
        Run the pipeline using the input data provided.

        If ``is_training`` is set to ``True`` then when it gets to the execution of the estimator,
        it will use the :meth:`surround.stage.Estimator.fit` method instead.

        If the above or ``batch_mode`` is set to ``True`` then when all the other stages have finished,
        the visualiser will be executed.

        If ``surround.enable_stage_output_dump`` is enabled in the Config instance then each filter and
        estimator's :meth:`surround.stage.Stage.dump_output` method will be called.

        This method doesn't return anything, instead results should be stored in the ``state``
        object passed in the parameters.

        If the ``set_stages`` method has been used, then instead of normal pipeline execution, it will
        instead execute the filters given in that method one by one.

        :param state: Data passed between each stage in the pipeline
        :type state: :class:`surround.State`
        :param is_training: Run the pipeline in training mode or not
        :type is_training: bool
        """

        LOGGER.info("Starting '%s'", self.assembler_name)

        no_stages = not self.estimator and not self.pre_filters and not self.post_filters
        no_stages = no_stages and not self.validator and not self.finaliser and not self.visualiser
        no_stages = no_stages and not self.stages
        if no_stages:
            LOGGER.warning("There are no stages to run!")

        if not state:
            raise ValueError("state is required to run an assembler")
        self.state = state

        if self.stages:
            self.__run_pipeline_stages()
        else:
            try:
                if self.validator:
                    self.__execute_validator(state)

                if self.state.errors:
                    LOGGER.error("Error while validating")
                    LOGGER.error(self.state.errors)
                else:
                    self.__run_pipeline(is_training)
            except Exception:
                LOGGER.exception("Failed running Assembler")
            finally:
                if self.finaliser:
                    self.__execute_finaliser(state)

    def __run_pipeline(self, is_training):
        """
        Executes the pre-filter(s), then the estimator (estimate/fit), then the post-filter(s)
        then the visualiser (only if ``is_training`` or ``batch_mode`` has been set).

        :param is_training: Run the pipeline in training mode or not
        :type is_training: bool
        """

        if self.pre_filters:
            if not self.__execute_filters(self.pre_filters, self.state):
                LOGGER.error("Failed running Assembler")
                return

        if self.estimator:
            if is_training:
                self.__execute_fit(self.state)
            else:
                self.__execute_main(self.state)

        if self.state.errors:
            LOGGER.error("Errors during executing the estimator")
            LOGGER.error(self.state.errors)
            return

        if self.post_filters:
            if not self.__execute_filters(self.post_filters, self.state):
                LOGGER.error("Failed running Assembler")
                return

        if (is_training or self.batch_mode) and self.visualiser:
            self.__execute_visualiser(self.state)

    def __run_pipeline_stages(self):
        """
        Executes the pipeline using the stages set to the assembler rather than the estimator workflow.
        """

        self.__execute_filters(self.stages, self.state)

    def __execute_validator(self, state):
        """
        Executes the validator on the data provided.
        Taking care of execution time tracking.

        :param state: data being passed through the pipeline
        :type state: :class:`surround.State`
        """

        stage_start = datetime.now()
        self.validator.validate(state, self.config)

        if self.config and self.config["surround"]["enable_stage_output_dump"]:
            self.validator.dump_output(state, self.config)

        # Calculate and log validator duration
        stage_execution_time = datetime.now() - stage_start
        state.stage_metadata.append({type(self.validator).__name__: str(stage_execution_time)})
        LOGGER.info("Validator %s took %s secs", type(self.validator).__name__, stage_execution_time)

    def __execute_finaliser(self, state):
        """
        Executes the finaliser on the data provided.
        Taking care of execution time tracking.

        :param state: data being passed through the pipeline
        :type state: :class:`surround.State`
        """

        stage_start = datetime.now()
        self.finaliser.operate(state, self.config)

        if self.config and self.config["surround"]["enable_stage_output_dump"]:
            self.finaliser.dump_output(state, self.config)

        # Calculate and log validator duration
        stage_execution_time = datetime.now() - stage_start
        state.stage_metadata.append({type(self.finaliser).__name__: str(stage_execution_time)})
        LOGGER.info("Finaliser %s took %s secs", type(self.finaliser).__name__, stage_execution_time)

    def __execute_visualiser(self, state):
        """
        Executes the visualiser on the data provided.
        Taking care of execution time tracking.

        :param state: data being passed through the pipeline
        :type state: :class:`surround.State`
        """

        stage_start = datetime.now()
        self.visualiser.visualise(state, self.config)

        if self.config and self.config["surround"]["enable_stage_output_dump"]:
            self.visualiser.dump_output(state, self.config)

        # Calculate and log validator duration
        stage_execution_time = datetime.now() - stage_start
        state.stage_metadata.append({type(self.visualiser).__name__: str(stage_execution_time)})
        LOGGER.info("Visualiser %s took %s secs", type(self.visualiser).__name__, stage_execution_time)

    def __execute_filters(self, filters, state):
        """
        Safely executes each filter in the list provided on the
        data provided and calculates time taken to execute the filters.

        :param filters: collection of filters to be executed
        :type filters: list of :class:`surround.stage.Filter`
        :param state: the data being filtered
        :type state: :class:`surround.State`
        :returns: whether execution succeeded
        :rtype: bool
        """

        state.freeze()
        start_time = datetime.now()

        try:
            for stage in filters:
                self.__execute_filter(stage, state)
                if state.errors:
                    LOGGER.error("Error during processing")
                    LOGGER.error(state.errors)
                    return False

            execution_time = datetime.now() - start_time
            state.execution_time = str(execution_time)
            LOGGER.info("Filter took %s secs", execution_time)
        except Exception:
            LOGGER.exception("Failed processing Surround Filters")
            return False

        state.thaw()
        return True

    def __execute_filter(self, stage, stage_data):
        """
        Executes a single filter on the data provided.
        Taking care of execution time tracking.

        :param stage: the filter
        :type stage: :class:`surround.stage.Filter`
        :param stage_data: data being filtered
        :type stage_data: :class:`surround.State`
        """

        stage_start = datetime.now()
        stage.operate(stage_data, self.config)

        if self.config and self.config["surround"]["enable_stage_output_dump"]:
            stage.dump_output(stage_data, self.config)

        # Calculate and log filter duration
        stage_execution_time = datetime.now() - stage_start
        stage_data.stage_metadata.append({type(stage).__name__: str(stage_execution_time)})
        LOGGER.info("Filter %s took %s secs", type(stage).__name__, stage_execution_time)

    def __execute_main(self, state):
        """
        Executes the :meth:`surround.stage.Estimator.estimate` method (used for
        batch-predict/predict mode), taking care of time tracking and dumping
        output (if requested).

        :param state: data being fed into the estimator
        :type state: :class:`surround.State`
        """

        main_start = datetime.now()
        self.estimator.estimate(state, self.config)

        if self.config and self.config["surround"]["enable_stage_output_dump"]:
            self.estimator.dump_output(state, self.config)

        # Calculate and log filter duration
        main_execution_time = datetime.now() - main_start
        state.stage_metadata.append({type(self.estimator).__name__: str(main_execution_time)})
        LOGGER.info("Estimator %s took %s secs", type(self.estimator).__name__, main_execution_time)

    def __execute_fit(self, state):
        """
        Executes the :meth:`surround.stage.Estimator.fit` method (used for training mode),
        taking care of time tracking and dumping output (if requested)

        :param state: data being fed into the estimator
        :type state: :class:`surround.State`
        """

        fit_start = datetime.now()
        self.estimator.fit(state, self.config)

        if self.config and self.config["surround"]["enable_stage_output_dump"]:
            self.estimator.dump_output(state, self.config)

        # Calculate and log filter duration
        fit_execution_time = datetime.now() - fit_start
        state.stage_metadata.append({type(self.estimator).__name__: str(fit_execution_time)})
        LOGGER.info("Fitting %s took %s secs", type(self.estimator).__name__, fit_execution_time)

    def load_config(self, module):
        """
        Given a module contained in the root of the project, create an instance of
        :class:`surround.config.Config` loading configuration data from the ``config.yaml``
        found in the project, and use this configuration for the pipeline.

        .. note:: Should be called before :meth:`surround.assembler.Assemble.init_assembler`

        :param module: name of the module
        :type module: str
        """

        if module:
            # Module already imported and has a file attribute
            mod = sys.modules.get(module)
            if mod and hasattr(mod, '__file__'):
                package_path = os.path.dirname(os.path.abspath(mod.__file__))
                root_path = os.path.dirname(package_path)
            else:
                raise ValueError("Invalid Python module %s" % module)

            self.set_config(Config(root_path))

            if not os.path.exists(self.config["output_path"]):
                os.makedirs(self.config["output_path"])
        else:
            self.set_config(Config())

        return self

    def set_config(self, config):
        """
        Set the configuration data to be used during pipeline execution.

        .. note:: Should be called before :meth:`surround.assembler.Assembler.init_assembler`.

        :param config: the configuration data
        :type config: :class:`surround.config.Config`
        """

        if not config or not isinstance(config, Config):
            raise TypeError("config should be of class Config")
        self.config = config

        return self

    def set_validator(self, validator):
        """
        Set the validator that will be executed before any other stage in the pipeline.
        The purpose of the validator is to check the contents of the state object to ensure
        it is valid for use in the pipeline.

        .. note:: Should be called before :meth:`surround.assembler.Assembler.init_assembler`.

        :param validator: the validator to be used for this pipeline
        :type validator: :class:`surround.stage.Validator`
        """

        if not isinstance(validator, Validator):
            raise ValueError("validator must be of class Validator")

        self.validator = validator

        return self

    def set_stages(self, stages):
        """
        Set the stages to be executed one after the other in the pipeline.

        .. note:: This cannot be used when the estimator has been set!

        :param stages: list of stages to execute
        :type stages: list of :class:`surround.stage.Filter`
        """

        if self.estimator:
            raise Exception("Cannot set stages when there is an estimator present!")

        if not isinstance(stages, list) or not all([isinstance(x, Filter) for x in stages]):
            raise ValueError("stages must be a list of Filter's only!")

        self.stages = stages

        return self

    def set_estimator(self, estimator, pre_filters=None, post_filters=None):
        """
        Set the estimator that should be used during pipeline execution and any filters (if required).

        .. note:: Should be called before :meth:`surround.assembler.Assembler.init_assembler`.

        :param estimator: the estimator to be used for this pipeline
        :type estimator: :class:`surround.stage.Estimator`
        :param pre_filters: list of pre-filters (default: None)
        :type pre_filters: :class:`list` of :class:`surround.stage.Filter`
        :param post_filters: list of post-filters (default: None)
        :type post_filters: :class:`list` of :class:`surround.stage.Filter`
        """

        if self.stages:
            raise Exception("Cannot set an estimator when their are stages present!")

        # Estimator is required
        if estimator is None:
            raise ValueError("estimator is not provided")
        if not isinstance(estimator, Estimator):
            raise TypeError("estimator should be of class Estimator")
        self.estimator = estimator

        if pre_filters:
            for pre_filter in pre_filters:
                if not isinstance(pre_filter, Filter):
                    raise TypeError("Pre-filter should be of class Filter")
        self.pre_filters = pre_filters

        if post_filters:
            for post_filter in post_filters:
                if not isinstance(post_filter, Filter):
                    raise TypeError("Post-filter should be of class Filter")
        self.post_filters = post_filters

        return self

    def set_pre_filters(self, pre_filters):
        """
        Set the filters that will be executed (in order) before the estimator in the pipeline.

        :param pre_filters: the filters
        :type: pre_filters: :class:`list` of :class:`surround.stage.Filter`
        """

        for pre_filter in pre_filters:
            if not isinstance(pre_filter, Filter):
                raise TypeError("Pre-filter should be of class Filter")

        self.pre_filters = pre_filters

        return self

    def set_post_filters(self, post_filters):
        """
        Set the filters that will be executed (in order) after the estimator in the pipeline.

        :param post_filters: the filters
        :type post_filters: :class:`list` of :class:`surround.stage.Filter`
        """

        for post_filter in post_filters:
            if not isinstance(post_filter, Filter):
                raise TypeError("Post-filter should be of class Filter")

        self.post_filters = post_filters

        return self

    def set_visualiser(self, visualiser):
        """
        Set the visualiser that will be executed after all other stages during
        batch-predict/training mode.

        .. seealso:: See :class:`surround.visualiser.Visualiser` for more information.

        :param visualiser: the visualiser instance
        :type visualiser: :class:`surround.visualiser.Visualiser`
        """

        # visualiser must be a type of Visualiser
        if not visualiser and not isinstance(visualiser, Visualiser):
            raise TypeError("visualiser should be of class Visualiser")
        self.visualiser = visualiser

        return self

    def set_finaliser(self, finaliser):
        """
        Set the final stage that will be executed no matter how the pipeline runs.
        This will be executed even when the pipeline fails or throws an error.

        :param finaliser: the final stage instance
        :type finaliser: :class:`surround.stage.Filter`
        """

        # finaliser must be a type of filter
        if not finaliser and not isinstance(finaliser, Filter):
            raise TypeError("finaliser should be of class Filter")
        self.finaliser = finaliser

        return self
