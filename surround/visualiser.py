from abc import ABC, abstractmethod
from .config import Config
from .surround import SurroundData

class Visualiser(ABC):
    """
    Base class for all visualisers that are executed at the end of a batch predict/training operation.

    Visualisers are used to prettify or format results from a batch predict or training execution
    of an :ref:`assembler`. Such as generating graphs or formatting the data in a way that is meaningful.

    .. note:: To set a visualiser to a pipeline, use :meth:`surround.assembler.Assembler.set_visualiser`.

    Example::

        import matplotlib.pyplot as plt

        class Accuracy(Visualiser):
            def visualise(self, surround_data, config):
                x = get_epochs(surround_data)
                y = get_accuracy_over_epochs(surround_data)

                plt.plot(x, y)
                plt.title("Epochs vs Accuracy")
                plt.xlabel("Epochs")
                plt.ylabel("Accuracy")
                plt.show()

        assembler = Assembler("Example", Validate(), Predict())
        assembler.set_visualiser(Accuracy())

        assembler.run(PipelineData(input_data))
    """

    @abstractmethod
    def visualise(self, surround_data: SurroundData, config: Config):
        """
        Prettify/format the data contained in ``surround_data``.

        Called by :meth:`surround.assembler.Assembler.run` after all other stages in
        the pipline have been executed.

        .. note:: This should only be called by the :ref:`assembler`!

        :param surround_data: Stores the results of the pipeline execution
        :type surround_data: Instance or child of :class:`surround.SurroundData`
        :param config: Config of the pipeline
        :type config: :class:`surround.config.Config`
        """
