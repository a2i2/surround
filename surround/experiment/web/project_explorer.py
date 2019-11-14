import os
import tornado.web

class ProjectExplorer(tornado.web.RequestHandler):
    def initialize(self, experiment_reader):
        self.experiment_reader = experiment_reader

    def get(self):
        projects = self.experiment_reader.get_projects()

        self.render(os.path.join(os.path.dirname(__file__), "project_explorer.html"), projects=projects)
