from abc import ABC, abstractmethod


class Visualiser(ABC):
    @abstractmethod
    def visualise(self, surround_data, config):
        """Prettify data

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of the SurroundData class
        :param config: Config of the pipeline
        :type config: <class 'surround.config.Config'>
        """
