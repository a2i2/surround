from abc import ABC, abstractmethod


class Stage(ABC):
    """
    Parent class of all Stages in a Surround pipleline. Provides the operate method which
    must be overridden by all stages.

    Public methods:
    - init_stage(config: Config)
    - operate(surround_data: SurroundData, config: Config)
    - dump_output(surround_data: SurroundData, config: Config)
    """

    def dump_output(self, surround_data, config):
        """
        Dump the output of the stage after the operate method has transformed the input data.

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of the SurroundData class
        :param config: Config of the pipeline
        :type config: <class 'surround.config.Config'>
        """

    @abstractmethod
    def operate(self, surround_data, config):
        """
        A stage in a surround pipeline.

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of the SurroundData class
        :param config: Contains the settings for each stage
        :type config: <class 'surround.config.Config'>
        """

    def init_stage(self, config):
        """
        Initialise the stage with some data or extra operations.

        :param config: Contains the settings for each stage
        :type config: <class 'surround.config.Config'>
        """
