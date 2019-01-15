from abc import ABC, abstractmethod


class Stage(ABC):

    @abstractmethod
    def operate(self, surround_data, config):
        """
        A stage in a surround.
        :param surround_data: Instance or child of the SurroundData class.
                              Stores intermediate data from each stage in Surround.
        :param config: A ConfigParser object that contains the settings for each stage.
        """
