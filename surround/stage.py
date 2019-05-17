from abc import ABC, abstractmethod


class Stage(ABC):
    """
    Parent class of all stages in a Surround pipeline.

    Stages main responsiblity are to transform input data in some way, this may be a
    data wrangling operation or a prediciton operation. This operation must happen in the
    :meth:`surround.stage.Stage.operate` method.

    Example::

        class DetectFaces(Stage):
            def init_stage(self, config):
                self.model = load_model(config["model-name"])

            def operate(self, data, config):
                data.faces = self.model.detect(data.input_image)

            def dump_output(self, data, config):
                print("Number of faces found: " + len(data.faces))

    """

    def dump_output(self, surround_data, config):
        """
        Dump the output of the stage after the operate method has transformed the input data.

        .. note:: This is called by :meth:`surround.Surround.process` (when dumping output is requested)

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of :class:`surround.SurroundData`
        :param config: Config of the pipeline
        :type config: :class:`surround.config.Config`
        """

    def init_stage(self, config):
        """Initialise stage with some data

        :param config: Contains the settings for each stage
        :type config: <class 'surround.config.Config'>
        """


class Validator(ABC):

    @abstractmethod
    def validate(self, surround_data, config):
        """Validate data being loaded into the pipeline.

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of the SurroundData class
        :param config: Config of the pipeline
        :type config: <class 'surround.config.Config'>
        """

class Filter(Stage):
    @abstractmethod
    def operate(self, surround_data, config):
        """Modify data before / after it enters Estimator.
        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of the SurroundData class
        :param config: Contains the settings for each stage
        :type config: <class 'surround.config.Config'>
        """

class Estimator(Stage):
    @abstractmethod
    def estimate(self, surround_data, config):
        """Process input data and return estimated values.

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of the SurroundData class
        :param config: Contains the settings for each stage
        :type config: <class 'surround.config.Config'>
        """
        
    def fit(self, surround_data, config):
        """Train a model.

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of the SurroundData class
        :param config: Contains the settings for each stage
        :type config: <class 'surround.config.Config'>
        """
