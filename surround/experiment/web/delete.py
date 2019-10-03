import tornado.web
import tornado.escape

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

    def post(self):
        data = tornado.escape.json_decode(self.request.body)

        if 'projectName' not in data or 'experiments' not in data:
            return

        for experiment in data['experiments']:
            self.experiment_writer.remove_experiment(data['projectName'], experiment)
