import os
import tornado.web

class ProjectExplorer(tornado.web.RequestHandler):
    def initialize(self, experiment_reader):
        self.experiment_reader = experiment_reader

    def get(self):
        projects = self.experiment_reader.get_projects()
        project_names = [proj['project_name'] for proj in projects]

        self.render(os.path.join(os.path.dirname(__file__), "project_explorer.html"), project_names=project_names, projects=projects)
