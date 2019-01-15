from abc import abstractmethod
from .stage import Stage

class Model(Stage):

    @abstractmethod
    def operate(self, surround_data, config):
        """A stage in a surround pipeline.

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of the SurroundData class
        :param config: Contains the settings for model
        :type config: <class 'surround.config.Config'>
        """

    @abstractmethod
    def fit(self, data, target, config):
        """Fit model according to data.

        :param data: Data to train on
        :param target: target values
        :param config: Config of the pipeline
        """

    def predict(self, data, config):
        """Predict using model.

        :param data: Data to predict
        :param config: Config of the pipeline
        """
