from abc import ABC, abstractmethod


class Stage(ABC):
    """
    Base class of all stages in a Surround pipeline.

    See the following class for more information:

    - :class:`surround.stage.Estimator`
    """

    def dump_output(self, state, config):
        """
        Dump the output of the stage after the stage has transformed the data.

        .. note:: This is called by :meth:`surround.assembler.Assembler.run` (when dumping output is requested).

        :param state: Stores intermediate data from each stage in the pipeline
        :type state: Instance or child of the :class:`surround.State` class
        :param config: Config of the pipeline
        :type config: :class:`surround.config.BaseConfig`
        """

    def operate(self, state, config):
        """
        Main function to be called in an assembly.
        :param state: Contains all pipeline state including input and output data
        :param config: Config for the assembly
        """

    def initialise(self, config):

        """
        Initialise the stage, this may be loading a model or loading data.

        .. note:: This is called by :meth:`surround.assembler.Assembler.init_assembler`.

        :param config: Contains the settings for each stage
        :type config: :class:`surround.config.BaseConfig`
        """

class Estimator(Stage):
    """
    Base class for an estimator in a Surround pipeline. Responsible for performing estimation
    or training using the input data.

    This stage is executed by :meth:`surround.assembler.Assembler.run`.

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
        :type config: :class:`surround.config.BaseConfig`
        """

    def fit(self, state, config):
        """
        Train a model using the input data.

        .. note:: This method is ONLY called by :meth:`surround.assembler.Assembler.run` when
                  running in training mode.

        :param state: Stores intermediate data from each stage in the pipeline
        :type state: Instance or child of the :class:`surround.State` class
        :param config: Contains the settings for each stage
        :type config: :class:`surround.config.BaseConfig`
        """
