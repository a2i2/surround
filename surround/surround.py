# surround.py
#
# Manages a set of stages and the data that is passed between them.
import logging
import sys
from enum import Enum

LOGGER = logging.getLogger(__name__)

class Frozen():
    """
    A class that can toggle the ability of adding new attributes.
    """
    __isfrozen = False
    def __setattr__(self, key, value):
        if self.__isfrozen and not hasattr(self, key):
            raise TypeError("%r is a frozen object" % self)
        object.__setattr__(self, key, value)

    def freeze(self):
        self.__isfrozen = True

    def thaw(self):
        self.__isfrozen = False


class SurroundData(Frozen):
    """
    Stores the data to be passed between each stage in Surround.
    Note that different stages inside Surround are responsible for
    setting the attributes.
    """
    stage_metadata = []
    execution_time = None
    errors = []
    warnings = []


class AllowedTypes(Enum):
    JSON = ["application/json"]
    FILE = ["file"]


class Wrapper():
    def __init__(self, surround, type_of_uploaded_object=None):
        self.surround = surround
        self.actual_type_of_uploaded_object = None
        if type_of_uploaded_object:
            self.type_of_uploaded_object = type_of_uploaded_object
        else:
            self.type_of_uploaded_object = AllowedTypes.JSON
        self.surround.init_stages()

    def run(self, input_data):
        if self.validate() is False:
            sys.exit()

    def validate(self):
        return self.validate_type_of_uploaded_object()
        # TODO: Find a way to validate_actual_type_of_uploaded_object(), probably using mime type # pylint: disable=fixme

    def validate_actual_type_of_uploaded_object(self):
        for type_ in self.type_of_uploaded_object.value:
            if self.actual_type_of_uploaded_object == type_:
                return True
        print("error: you selected input type as " + str(self.type_of_uploaded_object).split(".")[1])
        print("error: input file is not " + str(self.type_of_uploaded_object).split(".")[1])
        return False

    def validate_type_of_uploaded_object(self):
        for type_ in AllowedTypes:
            if self.type_of_uploaded_object == type_:
                return True
        LOGGER.info("error: selected upload type not allowed")
        LOGGER.info("Choose from: ")
        for type_ in AllowedTypes:
            LOGGER.info(type_)
        return False

    def process(self, input_data):
        Wrapper.run(self, input_data)
        return self.run(input_data)

    def get_config(self):
        return self.surround.config
