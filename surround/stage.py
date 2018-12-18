import abc

ABC = abc.ABCMeta('ABC', (object,), {'__slots__': ()})

class Stage(ABC):
    @abc.abstractmethod
    def operate(self, pipeline_data):
        """
            A stage in a pipeline.
            :param pipeline_data: Stores intermediate data from each stage in the pipeline. Implementations of this
            method should add stage output values to this object and return it as `pipeline_data`.
        """
        pass
