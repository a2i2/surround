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

    @abstractmethod
    def operate(self, surround_data, config):
        """
        Perform the intended operation of the stage. This method **must** be
        implemented in extensions of this class. Where it should perform some
        transformation/checking of the :attr:`surround_data`.

        .. note:: This is called by the :meth:`surround.Surround.process` method before/after other stages.

        :param surround_data: Stores intermediate data from each stage in the pipeline
        :type surround_data: Instance or child of :class:`surround.SurroundData`
        :param config: Contains the settings for each stage
        :type config: :class:`surround.config.Config`
        """

    def init_stage(self, config):
        """
        Initialise the stage with some data or extra operations. This method
        is called ONLY once before the stage is executed.

        For example you may load a Tensorflow model which you will use
        for prediction in the :meth:`surround.stage.Stage.operate` method.

        .. note:: This is called by the :meth:`surround.Surround.init_stages` method.

        :param config: Contains the settings for each stage
        :type config: :class:`surround.config.Config`
        """
