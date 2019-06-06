from abc import ABC, abstractmethod


class Loader(ABC):
    @abstractmethod
    def load(self, surround_data, config):
        """Load file(s) to be processed into the pipeline.

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of the SurroundData class
        :param config: Config of the pipeline
        :type config: <class 'surround.config.Config'>
        """

    @abstractmethod
    def execute(self, surround_data, config, run_pipeline):
        """Process each file(s) into a pipeline.

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of the SurroundData class
        :param config: Config of the pipeline
        :type config: <class 'surround.config.Config'>
        """
