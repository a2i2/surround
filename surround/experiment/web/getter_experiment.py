import tornado.web

class GetterExperiment(tornado.web.RequestHandler):
    def initialize(self, experiment_reader):
        self.reader = experiment_reader

    def get(self):
        project_name = self.get_argument("project_name", default=None)
        experiment_id = self.get_argument("experiment", default=None)

        experiment = self.reader.get_experiment(project_name, experiment_id)
        self.write(experiment)
