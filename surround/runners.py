from abc import ABC, abstractmethod


class Runner(ABC):
    def __init__(self, assembler):
        self.assembler = assembler

    @abstractmethod
    def run(self, is_training=False):
        """Execute assembler to process.
        """
