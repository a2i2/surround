from abc import ABC, abstractmethod
from .container import DataContainer
from .util import hash_zip, get_formats_from_files

class DataLinterStage(ABC):
    """
    Represents a stage in the Data Linter's linting pipeline.
    """

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.info = []
        self.warnings = []
        self.errors = []
        self.verbose = False

    def log_info(self, msg):
        """
        Log general information message to info list (print to terminal when verbose)

        :param msg: message to log
        :type msg: str
        """

        self.info.append(msg)

        if self.verbose:
            print(msg)

    def log_error(self, msg):
        """
        Log error message to errors list (print to terminal when verbose)

        :param msg: error message
        :type msg: str
        """

        self.errors.append(msg)

        if self.verbose:
            print("ERROR: %s" % msg)

    def log_warning(self, msg):
        """
        Log warningm message to warnings list (print to terminal when verbose)

        :param msg: warning message
        :type msg: str
        """

        self.warnings.append(msg)

        if self.verbose:
            print("WARNING: %s" % msg)

    @abstractmethod
    def execute(self, container, metadata):
        """
        Perform the checks this stage must do on the container and it's metadata.

        :param container: the data container being checked
        :type container: :class:`surround.data.container.DataContainer`
        :param metadata: the metadata of the container being checked
        :type metadata: :class:`surround.data.metadata.Metadata`
        """

class CheckDataIntegrity(DataLinterStage):
    """
    Represents the data integrity stage of the Data Linter.
    Checks whether the hash stored in the metadata matches the actual hash of the data in the container.
    """

    def __init__(self):
        super().__init__("Data Integrity", "Checks whether the contents of the container are the same as when it was genererated.")

    def execute(self, container, metadata):
        self.log_info("Calculating hash of the contents...")
        current_hash = hash_zip(container.path, skip_files=['manifest.yaml'])
        self.log_info("Calculated hash: %s" % current_hash)

        self.log_info("Comparing calculated hash with the hash in the metadata...")
        metadata_hash = metadata['summary']['identifier']

        if current_hash != metadata_hash:
            self.log_error("Hash mismatch detected!")
            self.log_error("The original contents of the container have changed since it was created!")
        else:
            self.log_info("OK!")

class CheckFormats(DataLinterStage):
    """
    Represents the format checking stage of the Data Linter.
    Checks whether the formats in the metadata match the formats in the actual container.
    """

    def __init__(self):
        super().__init__("Formats", "Checks whether the formats listed in the metadata are actually present in the container.")

    def execute(self, container, metadata):
        self.log_info("Detecting formats in content...")
        formats = get_formats_from_files(container.get_files())
        formats = set(formats)
        self.log_info("Done")

        metadata_formats = metadata['summary']['formats']
        metadata_formats = set(metadata_formats)

        self.log_info("Comparing detected formats with formats stored in metadata...")
        if formats == metadata_formats:
            self.log_info("OK!")
        else:
            self.log_error("Formats mismatch detected!")
            self.log_error("Formats detected:       %s" % formats)
            self.log_error("Formats from metadata:  %s" % metadata_formats)

class CheckMetadata(DataLinterStage):
    """
    Represents the metadata checking stage of the Data Linter.
    Checks whether the metadata contains the required fields and whether their values are the correct format.
    """

    def __init__(self):
        super().__init__("Metadata", "Checks whether the metadata contains the required fields and whether their values are the correct format.")

    def check_dictionary(self, schema, dictionary):
        for field, value in schema.items():
            typ, required, sub_schema = value

            prop_value = dictionary.get(field)

            if required and prop_value is None:
                self.log_error("Missing required field '%s'!" % field)
            elif prop_value is not None and not isinstance(prop_value, typ):
                self.log_error("Expected value type %s for field %s, got %s instead!" % (typ, field, type(prop_value)))
            elif sub_schema is not None and typ == list and prop_value is not None:
                self.check_list(sub_schema, prop_value)
            elif sub_schema is not None and typ == dict and prop_value is not None:
                self.check_dictionary(sub_schema, prop_value)

    def check_list(self, schema, elements):
        for obj in elements:
            self.check_dictionary(schema, obj)

    def execute(self, container, metadata):
        schema = metadata.SCHEMA

        version = metadata.get_property("version")
        if not version:
            self.log_error("No metadata version found in the manifest!")

        self.log_info("Checking metadata version...")
        if version in schema:
            self.log_info("OK!")
        else:
            self.log_error("Unable to find the version specified in the metadata file!")
            self.log_error("Version found: %s" % version)

        self.log_info("Checking the metadata against the schema...")
        schema = schema[version]

        for field, value in schema.items():
            typ, required, sub_schema = value

            prop_value = metadata.get_property(field)

            if required and prop_value is None:
                self.log_error("Missing required field '%s'!" % field)
            elif prop_value is not None and not isinstance(prop_value, typ):
                self.log_error("Expected value type %s for field %s, got %s instead!" % (typ, field, type(prop_value)))
            elif sub_schema is not None and typ == list and prop_value is not None:
                self.check_list(sub_schema, prop_value)
            elif sub_schema is not None and typ == dict and prop_value is not None:
                self.check_dictionary(sub_schema, prop_value)

        if not self.errors:
            self.log_info("OK!")

class DataLinter:
    """
    Represents the linter pipeline that checks the validity of the data container provided.
    """

    def __init__(self):
        self.info = []
        self.warnings = []
        self.errors = []
        self.stages = [CheckDataIntegrity(), CheckFormats(), CheckMetadata()]

    def list_stages(self):
        """
        List all of the stages in the pipeline to the terminal
        """

        print("============[Data Linter Stages]============")
        for i, stage in enumerate(self.stages):
            print("%i. %s - %s" % (i + 1, stage.name, stage.description))

    def lint(self, container_path, verbose=False, check_id=None):
        """
        Executes the linter on the provided data container, storing all messages in the
        info, warnings, and errors lists.

        :param container_path: path to the data container to lint
        :type container_path: str
        :param verbose: whether or not to print process to the terminal
        :type verbose: bool
        :param check_id: ID of a stage in the pipeline to run exclusively (all if None)
        :type check_id: int
        :returns: whether the data container is considered valid
        :rtype: bool
        """

        if verbose:
            print("==========[Running data linter]============")
            print("Performing checks on container: %s\n" % container_path)

        try:
            container = DataContainer(container_path)
        except Exception:
            self.errors.append("Failed to lint since the container failed to open!")
            if verbose:
                print(self.errors[0])

            return False

        metadata = container.metadata
        stages = [self.stages[check_id - 1]] if check_id is not None else self.stages

        for i, stage in enumerate(stages):
            # If we are just doing one check, skip all the rest
            if check_id is not None and check_id != i + 1:
                continue

            if verbose:
                print("============[Check #%i: %s]============" % (i + 1, stage.name))

            # Setup the stage
            stage.verbose = verbose
            stage.info.clear()
            stage.errors.clear()
            stage.warnings.clear()

            # Perform the linting stage
            stage.execute(container, metadata)

            if verbose:
                print()

            # Keep all results from the stage
            self.info.extend(stage.info)
            self.warnings.extend(stage.warnings)
            self.errors.extend(stage.errors)

        if verbose:
            passed = [stage for stage in stages if not stage.errors]
            print("%i/%i checks passed!" % (len(passed), len(stages)))

            if self.errors:
                print("Looks like there is something wrong with your container!")
            elif self.warnings:
                print("Looks like there are a couple minor issues with your container, but usable!")
            else:
                print("Your container looks good.")

            print("Goodbye.")

        return len(self.errors) > 0
