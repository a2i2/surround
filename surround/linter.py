import os
import io
from .stage import Filter, Estimator, Validator
from .surround import SurroundData
from .assembler import Assembler


class LinterStage(Filter):
    """
    Base class for a check in the Surround :class:`Linter`.

    Provides functions for creating warnings and errors that are
    found during the linting process.

    Example::

        class CheckExists(LinterStage):
            def operate(self, data, config):
                if not os.path.isdir(data.project_root):
                    self.add_error(data, "Project doesn't exist!")
    """

    def __init__(self, key, description):
        """
        Constructor for a linter stage.

        :param key: identifier of the linter stage
        :type key: str
        :param description: short description of the linter stage
        :type description: str
        """

        self.key = key
        self.description = description

    def add_error(self, data, string):
        """
        Creates an error which will be displayed and stop the :class:`Linter`.

        :param data: the data being passed between stages
        :type data: :class:`ProjectData`
        :param string: description of the error
        :type string: str
        """

        data.errors.append("ERROR: %s_CHECK: %s" % (self.key, string))

    def add_warning(self, data, string):
        """
        Creates a warning that will be displayed but the :class:`Linter` will continue.

        :param data: the data being passed between stages
        :type data: :class:`ProjectData`
        :param string: description of the warning
        :type string: str
        """

        data.warnings.append("WARNING: %s_CHECK: %s" % (self.key, string))

    def operate(self, surround_data, config):
        """
        Executed by the :class:`Linter`, performs the linting specific to this stage.
        **Must** be implemented in extended versions of this class.

        :param surround_data: the data being passed between stages
        :type surround_data: :class:`ProjectData`
        :param config: the configuration data for the linter
        :type config: :class:`surround.config.Config`
        """


class CheckData(LinterStage):
    """
    :class:`Linter` stage that checks the data folder in the surround project for files.
    """

    def __init__(self):
        LinterStage.__init__(self, "DATA", "Check data files")

    def operate(self, surround_data, config):
        """
        Executed by the :class:`Linter`, checks if there is any files in the project's data folder.
        If there is none then a warning will be issued.

        :param surround_data: the data being passed between stages
        :type surround_data: :class:`surround.SurroundData`
        :param config: the linter's configuration data
        :type config: :class:`surround.config.Config`
        """

        path = os.path.join(surround_data.project_root, "data")
        if not os.listdir(path):
            self.add_warning(surround_data, "No data available, data directory is empty")


class CheckFiles(LinterStage):
    """
    :class:`Linter` stage that checks the surround project files exist.
    """

    def __init__(self):
        LinterStage.__init__(self, "FILES", "Check for Surround project files")

    def operate(self, surround_data, config):
        """
        Executed by the :class:`Linter`, checks if the files in the project structure exist.
        Will create errors if required surround project files are missing in the root directory.

        :param surround_data: the data being passed between stages
        :type surround_data: :class:`surround.SurroundData`
        :param config: the linter's configuation data
        :type config: :class:`surround.config.Config`
        """

        for result in surround_data.project_structure["new"]["files"] + surround_data.project_structure["new"]["templates"]:
            file_name = result[0]
            path = os.path.join(
                surround_data.project_root,
                file_name.format(project_name=surround_data.project_name))


            if not os.path.isfile(path):
                if surround_data.project_type == "n" and os.path.basename(path) == "web_runner.py":
                    print("")
                else:    
                    self.add_error(surround_data, "Path %s does not exist" % path)


class CheckDirectories(LinterStage):
    """
    :class:`Linter` stage that checks the surround project directories exist.
    """

    def __init__(self):
        LinterStage.__init__(
            self, "DIRECTORIES",
            "Check for validating Surround's directory structure")

    def operate(self, surround_data, config):
        """
        Executed by the :class:`Linter`, checks whether the project directories exist.
        If the expected directories don't exist then errors will be created.

        :param surround_data: the data being passed between stages
        :type surround_data: :class:`surround.SurroundData`
        :param config: the linter's configuration data
        :type config: :class:`surround.config.Config`
        """

        for d in surround_data.project_structure["new"]["dirs"]:
            path = os.path.join(surround_data.project_root,
                                d.format(project_name=surround_data.project_name))
            if not os.path.isdir(path):
                self.add_error(surround_data, "Directory %s does not exist" % path)

class LinterValidator(Validator):
    """
    Linter's validator stage, checks the data given in the ProjectData is valid.
    """

    def validate(self, surround_data, config):
        """
        Executed by the :class:`Linter`, checks whther the paths contained are valid.

        :param surround_data: the data being passed between linter stages
        :type surround_data: :class:`surround.SurroundData`
        :param config: the linter's configuration data
        :type config: :class:`surround.config.Config`
        """

        if not isinstance(surround_data.project_name, str):
            surround_data.errors.append("ERROR: PROJECT_CHECK: Project name is not a string")

        if not isinstance(surround_data.project_structure, dict):
            surround_data.errors.append("ERROR: PROJECT_CHECK: Project structure invalid format")

        if not isinstance(surround_data.project_root, str):
            surround_data.errors.append("ERROR: PROJECT_CHECK: Project root path is not a string")

        if not isinstance(surround_data.project_type, str):
            surround_data.errors.append("ERROR: PROJECT_CHECK: Project type  is not a string")

class Main(Estimator):
    """
    Class responsible for executing all of the :class:`LinterStage`'s in the Surround Linter.
    """

    def __init__(self, filters):
        """
        :param filters: list of stages in the linter
        :type filters: list of :class:`LinterStage`
        """

        self.filters = filters

    def estimate(self, surround_data, config):
        """
        Execute each stage in the linter.
        """

        for filters in self.filters:
            filters.operate(surround_data, config)

    def fit(self, surround_data, config):
        """
        Should never be called.
        """

        print("No training implemented")


class ProjectData(SurroundData):
    """
    Class containing the data passed between each :class:`LinterStage`.

    **Attributes:**

    - :attr:`project_structure` - expected file structure of the surround project (:class:`dict`)
    - :attr:`project_root` - path to the root of the surround project (:class:`str`)
    - :attr:`project_name` - name of the surround project (:class:`str`)
    """

    def __init__(self, project_structure, project_root, project_name, project_type):
        """
        Constructor for the ProjectData class.

        :param project_structure: the expected file structure of the project
        :type project_structure: dict
        :param project_root: path to the root of the project
        :type project_root: str
        :param project_name: name of the project
        :type project_name: str
        """

        self.project_structure = project_structure
        self.project_root = project_root
        self.project_name = project_name
        self.project_type = project_type


class Linter():
    """
    Represents the Surround linter which performs multiple checks on the surround project
    and displays warnings/errors found during the linting process.

    This class is used by the Surround CLI to perform the linting of a project via the
    `lint` sub-command.

    To add a new check to the linter, append an instance of it to the ``filters`` list.
    """

    filters = [CheckDirectories(), CheckFiles(), CheckData()]

    def dump_checks(self):
        """
        Dumps a list of the checks in this linter.
        The list is compiled using the :attr:`LinterStage.key` and :attr:`LinterStage.description`
        attributes of each check.

        :return: formatted list of the checkers in the linter
        :rtype: str
        """
        with io.StringIO() as s:
            s.write("Checkers in Surround's linter\n")
            s.write("=============================")
            for stage in self.filters:
                s.write("\n%s - %s" % (stage.key, stage.description))
            output = s.getvalue()
        return output


    def check_project(self, project, project_root=os.curdir, project_type='n'):
        """
        Runs the linter against the project specified, returning any warnings/errors.

        :param project: expected file structure of the project
        :type project: dict
        :param project_root: path to the root of the project (default: current directory)
        :type project_root: str
        :return: errors and warnings found (if any)
        :rtype: (list of error strings, list of warning strings)
        """

        root = os.path.abspath(project_root)
        project_name = os.path.basename(root)
        data = ProjectData(project, root, project_name, project_type)
        assembler = Assembler("Linting", LinterValidator(), Main(self.filters))
        assembler.init_assembler()
        assembler.run(data)
        return data.errors, data.warnings
