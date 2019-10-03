import tornado.web

class Delete(tornado.web.RequestHandler):
    def initialize(self, experiment_reader, experiment_writer):
        self.experiment_reader = experiment_reader
        self.experiment_writer = experiment_writer

    def get(self):
        project_name = self.get_argument("project_name", default=None)

        if not project_name or not self.experiment_reader.has_project(project_name):
            self.redirect("./")

        self.experiment_writer.remove_project(project_name)
        self.redirect("./")
