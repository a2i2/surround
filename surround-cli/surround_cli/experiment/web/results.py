import tornado.web

class Results(tornado.web.RequestHandler):
    def initialize(self, experiment_reader):
        self.experiment_reader = experiment_reader

    def get(self):
        project_name = self.get_argument("project_name", default=None)
        start_time = self.get_argument("experiment", default=None)

        if not project_name or not start_time:
            self.redirect("./", permanent=True)

        results = self.experiment_reader.pull_experiment_file(project_name, start_time, "results.html")

        if results:
            results = results.decode('utf-8')
            self.write(results)
        else:
            self.redirect("./experiment?project_name=%s" % project_name)
