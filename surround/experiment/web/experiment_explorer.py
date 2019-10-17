import os
import tornado.web

class ExperimentExplorer(tornado.web.RequestHandler):
    def initialize(self, experiment_reader):
        self.experiment_reader = experiment_reader

    def get(self):
        project_name = self.get_argument("project_name", default=None)

        if not project_name:
            self.redirect("./", permanent=True)

        projects = self.experiment_reader.list_projects()
        project = self.experiment_reader.get_project(project_name)

        experiments = self.experiment_reader.list_experiments(project_name)
        experiments = sorted(experiments, reverse=True)

        self.render(os.path.join(os.path.dirname(__file__), "experiment_explorer.html"), project_names=projects, project=project, experiments=experiments)
