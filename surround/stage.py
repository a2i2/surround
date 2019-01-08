import abc

ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})

class Stage(ABC):

    def dump_output(self, dir, output):
        """
        Dump the output of each stage.

        :param dir: output directory
        :type dir: str
        :param output: output to dump
        :type output: depends on implementation
        """
        pass

    @abc.abstractmethod
    def operate(self, pipeline_data, config=None):
        """
        A stage in a pipeline.
        :param pipeline_data: Instance or child of the PipelineData class.
                              Stores intermediate data from each stage in the pipeline.
        :param config: A ConfigParser object that contains the settings for each stage.
        """
        pass
