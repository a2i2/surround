from abc import ABC, abstractmethod


class Runner(ABC):
    def __init__(self, assembler):
        self.assembler = assembler

    @abstractmethod
    def prepare_runner(self):
        """Setup pipeline entry points.
        This could be reading from file(s) or directory or a web service that listen for messages on specfic ports.
        """

    @abstractmethod
    def prepare_data(self):
        """Transform raw data coming from users into a format that is ready for assembler to process.
        This is a step before Surround pre-processing is called.
        """

    @abstractmethod
    def run(self, is_training=False):
        """Execute assembler to process.
        """
