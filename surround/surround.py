# surround.py
#
# Manages a set of stages and the data that is passed between them.
from importlib import import_module
import logging
import sys
import os
from enum import Enum
from datetime import datetime
from abc import ABC
from .stage import Stage
from .config import Config

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

class Surround(ABC):

    def __init__(self, surround_stages=None, module=None):
        self.surround_stages = surround_stages

        if module:
            # Module already imported and has a file attribute
            mod = sys.modules.get(module)
            if mod is not None and hasattr(mod, '__file__'):
                package_path = os.path.dirname(os.path.abspath(mod.__file__))
                root_path = os.path.dirname(package_path)
            else:
                raise ValueError("Invalid Python module %s" % module)

            self.set_config(Config(root_path))


            if not os.path.exists(self.config["output_path"]):
                os.makedirs(self.config["output_path"])
        else:
            self.set_config(Config())

    def set_config(self, config):
        if not config or not isinstance(config, Config):
            raise TypeError("config should be of class Config")
        self.config = config
        if self.config["surround"]["stages"]:
            self.surround_stages = []
            result = self.config.get_path(self.config["surround"]["stages"])
            if not isinstance(result, list):
                result = [result]
            for stage in filter(None, result):
                parts = stage.split(".")
                module = import_module("." + parts[-2], ".".join(parts[:-2]))
                klass = getattr(module, parts[-1])
                self.surround_stages.append(klass())

    def _execute_stage(self, stage, stage_data):
        stage_start = datetime.now()
        stage.operate(stage_data, self.config)

        if self.config["surround"]["enable_stage_output_dump"]:
            stage.dump_output(stage_data, self.config)

        # Calculate and log stage duration
        stage_execution_time = datetime.now() - stage_start
        stage_data.stage_metadata.append({type(stage).__name__: str(stage_execution_time)})
        LOGGER.info("Stage %s took %s secs", type(stage).__name__, stage_execution_time)

    def init_stages(self):
        for stage in self.surround_stages:
            stage.init_stage(self.config)

    def process(self, surround_data):
        assert isinstance(surround_data, SurroundData), \
            "Input must be a SurroundData object or inherit from SurroundData"

        surround_data.freeze()
        start_time = datetime.now()

        try:
            for stage in self.surround_stages:
                assert isinstance(stage, Stage), \
                    "A stage must be an instance of the Stage class"
                self._execute_stage(stage, surround_data)
                if surround_data.errors:
                    LOGGER.error("Error during processing")
                    LOGGER.error(surround_data.errors)
                    break
            execution_time = datetime.now() - start_time
            surround_data.execution_time = str(execution_time)
            LOGGER.info("Surround took %s secs", execution_time)
        except Exception:
            LOGGER.exception("Failed processing Surround")

        surround_data.thaw()

class AllowedTypes(Enum):
    JSON = "json"
    IMAGE = "image"

class Wrapper():
    def __init__(self, surround, type_of_uploaded_object=None):
        self.surround = surround
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

    def validate_type_of_uploaded_object(self):
        for type_ in AllowedTypes:
            if self.type_of_uploaded_object == type_:
                return True
        print("error: selected upload type not allowed")
        print("Choose from: ")
        for type_ in AllowedTypes:
            print(type_)
        return False

    def process(self, input_data):
        Wrapper.run(self, input_data)
        self.run(input_data)
