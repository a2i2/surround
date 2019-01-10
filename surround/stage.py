from abc import ABC, abstractmethod


class Stage(ABC):

    @abstractmethod
    def operate(self, pipeline_data, config=None):
        """
        A stage in a pipeline.
        :param pipeline_data: Instance or child of the PipelineData class.
                              Stores intermediate data from each stage in the pipeline.
        :param config: A ConfigParser object that contains the settings for each stage.
        """
