from abc import ABC, abstractmethod

class Wrapper(ABC):
    def __init__(self, surround, type_of_uploaded_object):
        self.surround = surround
        self.type_of_uploaded_object = type_of_uploaded_object
        self.surround.init_stages()

    @abstractmethod
    def run(self, uploaded_data):
        pass
