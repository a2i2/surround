import os
import io
from .stage import Stage
from .surround import SurroundData, Surround


class LinterStage(Stage):
    def __init__(self, key, description):
        self.key = key
        self.description = description

    def add_error(self, data, string):
        data.errors.append("ERROR: %s_CHECK: %s" % (self.key, string))

    def add_warning(self, data, string):
        data.warnings.append("WARNING: %s_CHECK: %s" % (self.key, string))

    def operate(self, surround_data, config):
        pass


class CheckData(LinterStage):
    def __init__(self):
        LinterStage.__init__(self, "DATA", "Check data files")

    def operate(self, surround_data, config):
        path = os.path.join(surround_data.project_root, "data")
        if not os.listdir(path):
            self.add_warning(surround_data, "No data available, data directory is empty")


class CheckFiles(LinterStage):
    def __init__(self):
        LinterStage.__init__(self, "FILES", "Check for Surround project files")

    def operate(self, surround_data, config):
        for result in surround_data.project_structure["new"][
                "files"] + surround_data.project_structure["new"]["templates"]:
            file_name = result[0]
            path = os.path.join(
                surround_data.project_root,
                file_name.format(project_name=surround_data.project_name))
            if not os.path.isfile(path):
                self.add_error(surround_data, "Path %s does not exist" % path)


class CheckDirectories(LinterStage):
    def __init__(self):
        LinterStage.__init__(
            self, "DIRECTORIES",
            "Check for validating Surround's directory structure")

    def operate(self, surround_data, config):
        for d in surround_data.project_structure["new"]["dirs"]:
            path = os.path.join(surround_data.project_root,
                                d.format(project_name=surround_data.project_name))
            if not os.path.isdir(path):
                self.add_error(surround_data, "Directory %s does not exist" % path)


class ProjectData(SurroundData):
    def __init__(self, project_structure, project_root, project_name):
        self.project_structure = project_structure
        self.project_root = project_root
        self.project_name = project_name


class Linter():

    linter_checks = Surround([CheckDirectories(), CheckFiles(), CheckData()])

    def dump_checks(self):
        with io.StringIO() as s:
            s.write("Checkers in Surround's linter\n")
            s.write("=============================")
            for stage in self.linter_checks.surround_stages:
                s.write("\n%s - %s" % (stage.key, stage.description))
            output = s.getvalue()
        return output


    def check_project(self, project, project_root=os.curdir):
        root = os.path.abspath(project_root)
        project_name = os.path.basename(root)
        data = ProjectData(project, root, project_name)
        self.linter_checks.process(data)
        return data.errors, data.warnings
