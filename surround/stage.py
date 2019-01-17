from abc import ABC, abstractmethod


class Stage(ABC):
    def dump_output(self, surround_data, config):
        """Dump the output of each stage.

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of the SurroundData class
        :param config: Config of the pipeline
        :type config: <class 'surround.config.Config'>
        """

    @abstractmethod
    def operate(self, surround_data, config):
        """A stage in a surround pipeline.

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of the SurroundData class
        :param config: Contains the settings for each stage
        :type config: <class 'surround.config.Config'>
        """

    def init_stage(self, config):
        """Initialise stage with some data

        :param config: Contains the settings for each stage
        :type config: <class 'surround.config.Config'>
        """
