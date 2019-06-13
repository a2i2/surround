# assembler.py

import sys
import os
import logging

from abc import ABC
from datetime import datetime

from .config import Config
from .visualiser import Visualiser
from .stage import Filter, Estimator, Validator

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

        config = Config()
        config.read_config_files(["config.yaml"])

        assembler = Assembler("Example pipeline", Validation(), None, config)
        assembler.set_estimator(PredictStage(), [PreFilter()], [PostFilter()])
        assembler.init_assembler(batch_mode=False)

        data = TestData("some data")
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
    def __init__(self, assembler_name="", validator=None, estimator=None, config=None):
        """
        Constructor for an Assembler pipeline:

        :param assembler_name: The name of the pipeline
        :type assembler_name: str
        :param validator: The validator to use on input data (default: None)
        :type validator: :class:`surround.stage.Validator`
        :param estimator: The estimator to use on input data (default: None)
        :type estimator: :class:`surround.stage.Estimator`
        :param config: The pipeline configuration data
        :type config: :class:`surround.config.Config`
        """

        if not validator:
            raise ValueError("'Validator' is required to run an assembler")
        if not isinstance(validator, Validator):
            raise TypeError("'validator' should be of class Validator")
        if estimator and not isinstance(estimator, Estimator):
            raise TypeError("'estimator' should be of class Estimator")
        if config and not isinstance(config, Config):
            raise TypeError("'config' should be of class Config")

        self.assembler_name = assembler_name
        self.config = config
        self.estimator = estimator
        self.validator = validator
        self.pre_filters = None
        self.post_filters = None
        self.visualiser = None
        self.batch_mode = False

    def init_assembler(self, batch_mode=False):
        """
        Initializes the assembler and all of it's stages.

        Calls the :meth:`surround.stage.Stage.init_stage` method of all filters and the estimator.
        Also used set the variable ``batch_mode`` which is then used to determine if the visualiser
        should be used after all the stages have been executed.

        .. note:: Should be called after :meth:`surround.assembler.Assembler.set_estimator` and
                :meth:`surround.assembler.Assembler.set_config`.

        :param batch_mode: Whether batch mode should be used
        :type batch_mode: bool
        """

        self.batch_mode = batch_mode
        try:
            if self.pre_filters:
                for pre_filter in self.pre_filters:
                    pre_filter.init_stage(self.config)

            self.estimator.init_stage(self.config)

            if self.post_filters:
                for post_filter in self.post_filters:
                    post_filter.init_stage(self.config)
        except Exception:
            LOGGER.exception("Failed initiating Assembler")

    def run(self, surround_data=None, is_training=False):
        """
        Run the pipeline using the input data provided.

        If ``is_training`` is set to ``True`` then when it gets to the execution of the estimator,
        it will use the :meth:`surround.stage.Estimator.fit` method instead.

        If the above or ``batch_mode`` is set to ``True`` then when all the other stages have finished,
        the visualiser will be executed.

        If ``surround.enable_stage_output_dump`` is enabled in the Config instance then each filter and
        estimator's :meth:`surround.stage.Stage.dump_output` method will be called.

        This method doesn't return anything, instead results should be stored in the ``surround_data``
        object passed in the parameters.

        :param surround_data: Data passed between each stage in the pipeline
        :type surround_data: :class:`surround.SurroundData`
        :param is_training: Run the pipeline in training mode or not
        :type is_training: bool
        """

        LOGGER.info("Starting '%s'", self.assembler_name)
        if not surround_data:
            raise ValueError("surround_data is required to run an assembler")
        self.surround_data = surround_data
        try:
            self.validator.validate(self.surround_data, self.config)
            self.__run_pipeline(is_training)
        except Exception:
            LOGGER.exception("Failed running Assembler")

    def __run_pipeline(self, is_training):
        """
        Executes the pre-filter(s), then the estimator (estimate/fit), then the post-filter(s)
        then the visualiser (only if ``is_training`` or ``batch_mode`` has been set).

        :param is_training: Run the pipeline in training mode or not
        :type is_training: bool
        """

        if self.pre_filters:
            self.__execute_filters(self.pre_filters, self.surround_data)

        if is_training:
            self.__execute_fit(self.surround_data)
        else:
            self.__execute_main(self.surround_data)

        if self.post_filters:
            self.__execute_filters(self.post_filters, self.surround_data)

        if (is_training or self.batch_mode) and self.visualiser:
            self.visualiser.visualise(self.surround_data, self.config)

    def __execute_filters(self, filters, surround_data):
        """
        Safely executes each filter in the list provided on the
        data provided and calculates time taken to execute the filters.

        :param filters: collection of filters to be executed
        :type filters: list of :class:`surround.stage.Filter`
        :param surround_data: the data being filtered
        :type surround_data: :class:`surround.SurroundData`
        """

        surround_data.freeze()
        start_time = datetime.now()

        try:
            for stage in filters:
                self.__execute_filter(stage, surround_data)
                if surround_data.errors:
                    LOGGER.error("Error during processing")
                    LOGGER.error(surround_data.errors)
                    break
            execution_time = datetime.now() - start_time
            surround_data.execution_time = str(execution_time)
            LOGGER.info("Filter took %s secs", execution_time)
        except Exception:
            LOGGER.exception("Failed processing Surround Filters")

        surround_data.thaw()

    def __execute_filter(self, stage, stage_data):
        """
        Executes a single filter on the data provided.
        Taking care of execution time tracking.

        :param stage: the filter
        :type stage: :class:`surround.stage.Filter`
        :param stage_data: data being filtered
        :type stage_data: :class:`surround.SurroundData`
        """

        stage_start = datetime.now()
        stage.operate(stage_data, self.config)

        if self.config and self.config["surround"]["enable_stage_output_dump"]:
            stage.dump_output(stage_data, self.config)

        # Calculate and log filter duration
        stage_execution_time = datetime.now() - stage_start
        stage_data.stage_metadata.append({type(stage).__name__: str(stage_execution_time)})
        LOGGER.info("Filter %s took %s secs", type(stage).__name__, stage_execution_time)

    def __execute_main(self, surround_data):
        """
        Executes the :meth:`surround.stage.Estimator.estimate` method (used for
        batch-predict/predict mode), taking care of time tracking and dumping
        output (if requested).

        :param surround_data: data being fed into the estimator
        :type surround_data: :class:`surround.SurroundData`
        """

        main_start = datetime.now()
        self.estimator.estimate(surround_data, self.config)

        if self.config and self.config["surround"]["enable_stage_output_dump"]:
            self.estimator.dump_output(surround_data, self.config)

        # Calculate and log filter duration
        main_execution_time = datetime.now() - main_start
        surround_data.stage_metadata.append({type(self.estimator).__name__: str(main_execution_time)})
        LOGGER.info("Estimator %s took %s secs", type(self.estimator).__name__, main_execution_time)


    def __execute_fit(self, surround_data):
        """
        Executes the :meth:`surround.stage.Estimator.fit` method (used for training mode),
        taking care of time tracking and dumping output (if requested)

        :param surround_data: data being fed into the estimator
        :type surround_data: :class:`surround.SurroundData`
        """

        fit_start = datetime.now()
        self.estimator.fit(surround_data, self.config)

        if self.config and self.config["surround"]["enable_stage_output_dump"]:
            self.estimator.dump_output(surround_data, self.config)

        # Calculate and log filter duration
        fit_execution_time = datetime.now() - fit_start
        surround_data.stage_metadata.append({type(self.estimator).__name__: str(fit_execution_time)})
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

    def set_estimator(self, estimator=None, pre_filters=None, post_filters=None):
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

        # Estimator is required
        if estimator is None:
            raise ValueError("estimator is not provided")
        if not isinstance(estimator, Estimator):
            raise TypeError("estimator should be of class Estimator")
        self.estimator = estimator

        if pre_filters:
            for pre_filter in pre_filters:
                if not isinstance(pre_filter, Filter):
                    raise TypeError("Prefilter should be of class Filter")
        self.pre_filters = pre_filters

        if post_filters:
            for post_filter in post_filters:
                if not isinstance(post_filter, Filter):
                    raise TypeError("post_filter should be of class Filter")
        self.post_filters = post_filters

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
