import os
import io
from .stage import Stage
from .surround import SurroundData, Surround


class LinterStage(Stage):
    """
    Base class for a stage in the surround linter.

    Public methods:
    - add_error(data: SurroundData, string)
    - add_warning(data: surroundData, string)
    - operate(surround_data: SurroundData, config: Config)
    """

    def __init__(self, key, description):
        """
        Constructor for a linter stage.

        :param key: identifier of the linter stage
        :type key: string
        :param description: short description of the linter stage
        :type description: string
        """

        self.key = key
        self.description = description

    def add_error(self, data, string):
        """
        Creates an error which will be displayed and stop the linter.

        :param data: the data being passed between stages
        :type data: <class 'surround.surround.SurroundData'>
        :param string: description of the error
        :type string: string
        """

        data.errors.append("ERROR: %s_CHECK: %s" % (self.key, string))

    def add_warning(self, data, string):
        """
        Creates a warning that will be displayed but the linter will continue.

        :param data: the data being passed between stages
        :type data: <class 'surround.surround.SurroundData'>
        :param string: description of the warning
        :type string: string
        """

        data.warnings.append("WARNING: %s_CHECK: %s" % (self.key, string))

    def operate(self, surround_data, config):
        """
        Executed by the linter, performs the linting specific to this stage.

        :param surround_data: the data being passed between stages
        :type data: <class 'surround.surround.SurroundData'>
        :param config: the configuration data for the linter
        :type config: <class 'surround.config.Config'>
        """


class CheckData(LinterStage):
    """
    Linter stage that checks the data folder for files.

    Public methods:
    - operate(surround_data: SurroundData, config: Config)
    """

    def __init__(self):
        """
        Constructor for the CheckData linter stage.
        """

        LinterStage.__init__(self, "DATA", "Check data files")

    def operate(self, surround_data, config):
        """
        Executed by the linter, checks if there is any files in the project's data folder. 

        :param surround_data: the data being passed between stages
        :type surround_data: <class 'surround.surround.SurroundData'>
        :param config: the linter's configuration data
        :type config: <class 'surround.config.Config'>
        """

        path = os.path.join(surround_data.project_root, "data")
        if not os.listdir(path):
            self.add_warning(surround_data, "No data available, data directory is empty")


class CheckFiles(LinterStage):
    """
    Linter stage that checks the surround project files exist. 

    Public methods:
    - operate(surround_data: SurroundData, config: Config)
    """

    def __init__(self):
        """
        Constructor for the CheckFiles linter stage.
        """

        LinterStage.__init__(self, "FILES", "Check for Surround project files")

    def operate(self, surround_data, config):
        """
        Executed by the linter, checks if the files in the project structure exist.

        :param surround_data: the data being passed between stages
        :type surround_data: <class 'surround.surround.SurroundData'>
        :param config: the linter's configuation data
        :type config: <class 'surround.config.Config'>
        """
  
        for result in surround_data.project_structure["new"]["files"] + surround_data.project_structure["new"]["templates"]:
            file_name = result[0]
            path = os.path.join(
                surround_data.project_root,
                file_name.format(project_name=surround_data.project_name))
            if not os.path.isfile(path):
                self.add_error(surround_data, "Path %s does not exist" % path)


class CheckDirectories(LinterStage):
    """
    Linter stage that checks the surround project directories exist.

    Public methods:
    - operate(surround_data: SurroundData, config: Config)
    """

    def __init__(self):
        """
        Constructor for the CheckDirectories linter stage.
        """

        LinterStage.__init__(
            self, "DIRECTORIES",
            "Check for validating Surround's directory structure")

    def operate(self, surround_data, config):
        """
        Executed by the linter, checks whether the project directories exist.

        :param surround_data: the data being passed between stages
        :type surround_data: <class 'surround.surround.SurroundData'>
        :param config: the linter's configuration data
        :type config: <class 'surround.config.Config'>
        """

        for d in surround_data.project_structure["new"]["dirs"]:
            path = os.path.join(surround_data.project_root,
                                d.format(project_name=surround_data.project_name))
            if not os.path.isdir(path):
                self.add_error(surround_data, "Directory %s does not exist" % path)


class ProjectData(SurroundData):
    """
    Class containing the data passed between linter stages.
    """

    def __init__(self, project_structure, project_root, project_name):
        """
        Constructor for the ProjectData class.

        :param project_structure: the expected file structure of the project
        :type project_structure: dictionary
        :param project_root: path to the root of the project
        :type project_root: string
        :param project_name: name of the project
        :type project_name: string
        """

        self.project_structure = project_structure
        self.project_root = project_root
        self.project_name = project_name


class Linter():
    """
    Represents the linter which performs multiple checks on the surround project
    and displays warnings/errors found during the linting process.

    Public methods:
    - dump_checks()
    - check_project(project, project_root)
    """

    linter_checks = Surround([CheckDirectories(), CheckFiles(), CheckData()])

    def dump_checks(self):
        """
        Dumps a list of the checks performed by the linter.

        :return: formatted list of the checkers in the linter
        :rtype: string
        """
        with io.StringIO() as s:
            s.write("Checkers in Surround's linter\n")
            s.write("=============================")
            for stage in self.linter_checks.surround_stages:
                s.write("\n%s - %s" % (stage.key, stage.description))
            output = s.getvalue()
        return output


    def check_project(self, project, project_root=os.curdir):
        """
        Runs the linter against the project specified, returning any warnings/errors.

        :param project: expected file structure of the project
        :type project: dictionary
        :param project_root: path to the root of the project (default: current directory)
        :type project_root: string
        :return: errors and warnings found (if any)
        :rtype: list of error strings, list of warning strings
        """

        root = os.path.abspath(project_root)
        project_name = os.path.basename(root)
        data = ProjectData(project, root, project_name)
        self.linter_checks.process(data)
        return data.errors, data.warnings
