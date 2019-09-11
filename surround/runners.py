from abc import ABC, abstractmethod
from enum import Enum

from .state import State

class RunMode(Enum):
    BATCH_PREDICT = 1
    PREDICT = 2
    TRAIN = 3
    WEB = 4

class Runner(ABC):
    """
    Base class for runners which are responsible for:

    - Initializing an :class:`surround.assembler.Assembler`.
    - Loading/preparing input data.
    - Running the :class:`surround.assembler.Assembler`.

    Example batch runner::

        class BatchRunner(Runner):
            def load_data(self, mode, config):
                state = AssemblyState()

                if mode == RunMode.TRAIN:
                    state.input_data = load_files('training_set')
                else:
                    state.input_data = load_files('predict_set')

                return state

    .. note:: You get a Batch Runner and Web Runner (if web requested) when
              you generate a project using the CLI tool.
    """

    def __init__(self, assembler):
        """
        :param assembler: The assembler the runner will execute
        :type assembler: :class:`surround.assembler.Assembler`
        """

        self.assembler = assembler

    @abstractmethod
    def load_data(self, mode, config):
        """
        Load the data and prepare it to be fed into the :class:`surround.assembler.Assembler`.

        :param mode: the mode the assembly was run in (batch, train, predict, web)
        :type mode: :class:`surround.runners.RunMode`
        :param config: the configuration of the assembly
        :type config: :class:`surround.config.Config`
        """

    def run(self, mode=RunMode.BATCH_PREDICT):
        """
        Prepare data and execute the :class:`surround.assembler.Assembler`.

        :param is_training: Run the pipeline in training mode or not
        :type is_training: bool
        """

        # Initialise the assembler
        self.assembler.init_assembler(mode == RunMode.BATCH_PREDICT)

        # Load the data to be fed into the assembler
        data = self.load_data(mode, self.assembler.config)

        if not isinstance(data, State):
            raise ValueError("load_data must return an instance of State!")

        # Run assembler
        self.assembler.run(data, mode == RunMode.TRAIN)
