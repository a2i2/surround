from abc import ABC, abstractmethod


class Stage(ABC):
    def dump_output(self, output_dir, output, config):
        """Dump the output of each stage.

        :param output_dir: Output directory
        :type output_dir :str
        :param output: Output to dump
        :type output: Same as surround_data (depends on implementation)
        :param config: Config of the pipeline
        :type config: <class 'surround.config.Config'>
        """

    @abstractmethod
    def operate(self, surround_data, config):
        """
        A stage in a surround.
        :param surround_data: Instance or child of the SurroundData class.
                              Stores intermediate data from each stage in Surround.
        :param config: A ConfigParser object that contains the settings for each stage.
        """
