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
    When the class is considered frozen, adding new attributes will
    trigger a :exc:`TypeError` exception.
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
    Stores the data to be passed between each stage in a pipeline.
    Each stage is responsible for setting the attributes to this class.

    **Attributes:**

    - `stage_metadata` (:class:`list`) - information that can be used to identify the stage
    - `execution_time` (:class:`str`) - how long it took to execute the entire pipeline
    - `errors` (:class:`list`) - list of error messages (stops the pipeline when appended to)
    - `warnings` (:class:`list`) - list of warning messages (displayed in console)

    Example::

        class PipelineData(SurroundData):
            # Extra attributes must be defined before the pipeline is ran!
            input_data = None
            output_data = None

            def __init__(self, input_data)
                self.input_data = input_data

        class ValidationStage(Stage):
            def operate(self, data, config):
                if not isinstance(data.input_data, str):
                    data.errors.append('not correct input format!')
                elif len(data.input_data) == 0:
                    data.warnings.append('input is empty')

        pipeline = Surround([ValidationStage(), PredictStage()])
        data = PipelineData("received data")
        pipeline.process(data)

        print(data.output_data)

    .. note::
        This class is frozen when the pipeline is being ran.
        This means that an exception will be thrown if a new attribute
        is added during pipeline execution.
    """

    stage_metadata = []
    execution_time = None
    errors = []
    warnings = []

class Surround(ABC):
    """
    Represents an entire Surround pipeline, containing all the stages and configuration.

    Responsibilties:

    - Store and initialize all the stages
    - Store the Config instance used by all the stages
    - Perform operations on input data by executing each stage on the data
    - Dump the output of each stage (if requested in the Config)

    Example::

        pipeline = Surround([ValidateStage(),
                             FaceDetectionStage(),
                             ExtractFaceStage()])

        config = Config()
        config.read_config_files(["config.yaml"])
        pipeline.set_config(config)

        data = PipelineData(image)
        pipeline.process(data)

        save_image(data.output_image)
    """

    def __init__(self, surround_stages=None, module=None):
        """
        Constructs an instance of a Surround pipeline.

        :param surround_stages: the surround stages to be executed in this pipeline (default: None)
        :type surround_stages: a list of :class:`surround.stage.Stage`
        :param module: name of the module that is creating this instance (used to get root directory)
        :type module: str
        """

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
        """
        Sets the config instance used in all stages during execution of the pipeline.
        Ensures order of stages set in the Config instance is followed (if set).

        :param config: instance containing configuration data
        :type config: :class:`surround.config.Config`
        """

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
        """
        Executes the provided stage with data, dumping output (if requested) and logging execution time.

        :param stage: the stage you would like to execute
        :type stage: :class:`surround.stage.Stage`
        :param stage_data: the data that is being transformed by the stage
        :type stage_data: :class:`SurroundData`
        """

        stage_start = datetime.now()
        stage.operate(stage_data, self.config)

        if self.config["surround"]["enable_stage_output_dump"]:
            stage.dump_output(stage_data, self.config)

        # Calculate and log stage duration
        stage_execution_time = datetime.now() - stage_start
        stage_data.stage_metadata.append({type(stage).__name__: str(stage_execution_time)})
        LOGGER.info("Stage %s took %s secs", type(stage).__name__, stage_execution_time)

    def init_stages(self):
        """
        Initializes all stages in the pipeline by calling their :meth:`surround.stage.Stage.init_stage` method.
        """

        for stage in self.surround_stages:
            stage.init_stage(self.config)

    def process(self, surround_data):
        """
        Run the entire pipeline with the provided data and log the execution time.

        .. note::
            The `surround_data` object will be frozen while this process completes.
            Meaning no *new* attributes can be added to the object (or an exception will be thrown).

        :param surround_data: the data we are feeding through the pipeline
        :type surround_data: a child or instance of :class:`SurroundData`
        """

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
    """
    Enumeration for types allowed as input to a pipeline via the :class:`Wrapper`.

    - :attr:`AllowedTypes.JSON` - Accept JSON data only
    - :attr:`AllowedTypes.FILE` - Accept files only
    """

    JSON = ["application/json"]
    FILE = ["file"]

class Wrapper():
    """
    Parent class for wrappers which handle the execution of a pipeline.
    Extensions of this class are used to execute the pipeline both locally and over the web
    via the Surround CLI.

    Your extended class **must** be added to the projects `config.yaml` file as `wrapper-info`
    so that the Surround CLI can find and use your wrapper when running in web-server mode.

    For example (in `config.yaml`)::

        wrapper-info: testproject.wrapper.PipelineWrapper

    Your extension must implement the :meth:`Wrapper.run` method which should setup the
    input data and run the :meth:`Surround.process` method of the pipeline.
    """

    def __init__(self, surround, type_of_uploaded_object=None):
        """
        Constructor of the Wrapper initializes the stages of the provided pipeline.

        :param surround: the surround pipeline the wrapper will manage
        :type surround: :class:`Surround`
        :param type_of_uploaded_object: type of data the pipeline will accept
        :type type_of_uploaded_object: :class:`AllowedTypes`
        """

        self.surround = surround
        self.actual_type_of_uploaded_object = None
        if type_of_uploaded_object:
            self.type_of_uploaded_object = type_of_uploaded_object
        else:
            self.type_of_uploaded_object = AllowedTypes.JSON
        self.surround.init_stages()

    def run(self, input_data):
        """
        Runs the surround pipeline with the given input data.
        This method should be extended to convert the input data and execute the pipeline.

        .. note:: Called by the :meth:`Wrapper.process` method.

        For example::

            def run(self, input_data):
                data = SurroundData(json.loads(input_data))
                output = self.surround.process(data)

                return output


        :param input_data: the input data to be put through the pipeline
        :type input_data: any
        :return: the transformed data after execution of the pipeline
        :rtype: any
        """

        if self.validate() is False:
            sys.exit()

    def validate(self):
        """
        Validates the configuration of the pipeline and the type of the input data.

        :return: True on success, False on failure
        :rtype: bool
        """

        return self.validate_type_of_uploaded_object()
        # TODO: Find a way to validate_actual_type_of_uploaded_object(), probably using mime type # pylint: disable=fixme

    def validate_actual_type_of_uploaded_object(self):
        """
        Validate the actual type of the input with the selected type of input.

        :return: True if the types match, False otherwise
        :rtype: bool
        """

        for type_ in self.type_of_uploaded_object.value:
            if self.actual_type_of_uploaded_object == type_:
                return True
        print("error: you selected input type as " + str(self.type_of_uploaded_object).split(".")[1])
        print("error: input file is not " + str(self.type_of_uploaded_object).split(".")[1])
        return False

    def validate_type_of_uploaded_object(self):
        """
        Validate selected input type against allowed types.

        :return: True if selected type allowed, False otherwise
        :rtype: bool
        """

        for type_ in AllowedTypes:
            if self.type_of_uploaded_object == type_:
                return True
        LOGGER.info("error: selected upload type not allowed")
        LOGGER.info("Choose from: ")
        for type_ in AllowedTypes:
            LOGGER.info(type_)
        return False

    def process(self, input_data):
        """
        Runs the surround pipeline with the given input data, ensuring the pipeline is validated first.
        This is called when running the pipeline via web endpoints.

        :param input_data: input data that will be fed through the pipeline
        :type input_data: any
        :return: the result of the run method (typically output data)
        :rtype: any
        """

        Wrapper.run(self, input_data)
        return self.run(input_data)

    def get_config(self):
        """
        Returns the configuration data of the surround pipeline.

        :return: the data used to configure the pipeline
        :rtype: :class:`surround.config.Config`
        """

        return self.surround.config
