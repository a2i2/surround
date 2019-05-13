# surround.py
#
# Manages a set of stages and the data that is passed between them.
import logging

LOGGER = logging.getLogger(__name__)

class Frozen():
    """
    A class that can toggle the ability of adding new attributes.

    Public methods:
    - freeze()
    - thaw()
    """

    __isfrozen = False

    def __setattr__(self, key, value):
        """
        Called when an attribute is created/modified, throws an exception when frozen and adding a new attribute.
        Otherwise sets the attribute at the provided key to the provided value.

        :param key: the name of the attribute
        :type key: string
        :param value: the new value of the attribute
        :type value: any
        """

        if self.__isfrozen and not hasattr(self, key):
            raise TypeError("%r is a frozen object" % self)
        object.__setattr__(self, key, value)

    def freeze(self):
        """
        Freeze this class, throw exceptions from now on when a new attribute is added.
        """

        self.__isfrozen = True

    def thaw(self):
        """
        Thaw the class, no longer throw exceptions on new attributes.
        """

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
