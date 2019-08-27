from abc import ABC, abstractmethod


class Stage(ABC):
    """
    Base class of all stages in a Surround pipeline.

    See the following classes for more information:

    - :class:`surround.stage.Estimator`
    - :class:`surround.stage.Filter`
    """

    def dump_output(self, state, config):
        """
        Dump the output of the stage after the stage has transformed the data.

        .. note:: This is called by :meth:`surround.assembler.Assembler.run` (when dumping output is requested).

        :param state: Stores intermediate data from each stage in the pipeline
        :type state: Instance or child of the :class:`surround.State` class
        :param config: Config of the pipeline
        :type config: :class:`surround.config.Config`
        """

    def initialise(self, config):
        """
        Initialise the stage, this may be loading a model or loading data.

        .. note:: This is called by :meth:`surround.assembler.Assembler.init_assembler`.

        :param config: Contains the settings for each stage
        :type config: :class:`surround.config.Config`
        """

class Validator(ABC):
    """
    Base class of a validation stage in a Surround pipeline. Responsible for checking the data being
    fed into the pipeline before passing the data onto the next stages (filtering, estimation, etc).

    .. note:: This stage is executed in :meth:`surround.assembler.Assembler.run` before all other stages in the pipeline.

    Example::

        class InputValidator(Validator):
            def validate(self, state, config):
                if not state.input_data:
                    # Stop the pipeline, we have no data!
                    state.errors.append("'input_data' is None")
    """

    @abstractmethod
    def validate(self, state, config):
        """
        Validate data being loaded into the pipeline. Appending to ``state.errors``
        or ``state.warnings`` when problems are found with the input data.

        .. note:: This should only be called by :meth:`surround.assembler.Assembler.run`.

        :param state: Stores intermediate data from each stage in the pipeline
        :type state: Instance or child of the :class:`surround.State` class
        :param config: Config of the pipeline
        :type config: :class:`surround.config.Config`
        """

class Filter(Stage):
    """
    Base class of all filters (pre or post) in a Surround pipeine.

    There are two types of filters:

    - **Pre-filters** - Perform data wrangling operations on the data **before**
                        being fed into an :class:`surround.stage.Estimator`.
    - **Post-filters** - Perform data wrangling operations on the data **after**
                        being fed into an :class:`surround.stage.Estimator`.

    Depending on the type, this stage is executed before/after an estimator in the pipeline.

    There can be many pre/post filters in a single :class:`surround.assembler.Assembler` instance.

    .. note:: To set the pre/post filter(s), use :meth:`surround.assembler.Assembler.set_estimator`.

    Example::

        class ConvertFromJSONString(Filter):
            def operate(self, state, config):
                state.input_data = json.loads(self.input_data)

        class ConvertToJSONString(Filter):
            def operate(self, state, config):
                state.output_data = json.dumps(self.input_data)

        assembler = Assembler("Example", ValidationStage())

        # Set ConvertFromJSONString as a pre-filter, the other as a post-filter
        assembler.set_estimator(PredictStage, [ConvertFromJSONString()], [ConvertToJSONString()])

        data = PipelineData("{ \"example\": \"data\" }")
        assembler.run(data)

        # Would print JSON represented as a string
        print(data.output_data)
    """

    @abstractmethod
    def operate(self, state, config):
        """
        Modify data before/after it enters an :class:`surround.stage.Estimator`.

        .. note:: This should only be called by :meth:`surround.assembler.Assembler.run`.

        :param state: Stores intermediate data from each stage in the pipeline
        :type state: Instance or child of the :class:`surround.State` class
        :param config: Contains the settings for each stage
        :type config: :class:`surround.config.Config`
        """

class Estimator(Stage):
    """
    Base class for an estimator in a Surround pipeline. Responsible for performing estimation
    or training using the input data.

    This stage is executed by :meth:`surround.assembler.Assembler.run` after the validator and
    in-between pre and post filters.

    Example::

        class Predict(Estimator):
            def initialise(self, config):
                self.model = load_model(os.path.join(config["models_path"], "model.pb"))

            def estimate(self, state, config):
                state.output_data = run_model(self.model)

            def fit(self, state, config):
                state.output_data = train_model(self.model)
    """

    @abstractmethod
    def estimate(self, state, config):
        """
        Process input data and store estimated values.

        .. note:: This method is ONLY called by :meth:`surround.assembler.Assembler.run` when
                  running in predict/batch-predict mode.

        :param state: Stores intermediate data from each stage in the pipeline
        :type state: Instance or child of the :class:`surround.State` class
        :param config: Contains the settings for each stage
        :type config: :class:`surround.config.Config`
        """

    def fit(self, state, config):
        """
        Train a model using the input data.

        .. note:: This method is ONLY called by :meth:`surround.assembler.Assembler.run` when
                  running in training mode.

        :param state: Stores intermediate data from each stage in the pipeline
        :type state: Instance or child of the :class:`surround.State` class
        :param config: Contains the settings for each stage
        :type config: :class:`surround.config.Config`
        """
