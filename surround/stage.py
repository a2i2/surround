from abc import ABC, abstractmethod


class Stage(ABC):

    def dump_output(self, output_dir, output, config=None):
        """
        Dump the output of each stage.

        :param output_dir: output directory
        :type output_dir: str
        :param output: output to dump
        :type output: depends on implementation
        :param config: Contains the settings for each stage.
        :type config: ConfigParser object
        """

    @abstractmethod
    def operate(self, pipeline_data, config=None):
        """
        A stage in a pipeline.

        :param pipeline_data: Stores intermediate data from each stage in the pipeline.
        :type pipeline_data: Instance or child of the PipelineData class
        :param config: Contains the settings for each stage.
        :type config: ConfigParser object
        """
