from abc import ABC, abstractmethod

class Wrapper(ABC):
    def __init__(self, surround):
        self.surround = surround
        self.surround.init_stages()

    @abstractmethod
    def run(self, uploaded_data):
        pass
