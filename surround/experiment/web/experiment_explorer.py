import os
import tornado.web

class ExperimentExplorer(tornado.web.RequestHandler):
    def initialize(self, experiment_reader):
        self.experiment_reader = experiment_reader

    def get(self):
        project_name = self.get_argument("project_name", default=None)

        if not project_name:
            self.redirect("./", permanent=True)

        projects = self.experiment_reader.get_projects()
        project = self.experiment_reader.get_project(project_name)
        experiments = self.experiment_reader.get_experiments(project_name)
        experiments = sorted(experiments, key=lambda x: x['execution_info']['start_time'], reverse=True)

        metric_names = []
        for exp in experiments:
            if exp["results"]:
                metrics = exp["results"]["metrics"]
                metric_names.extend(metrics.keys())

        metric_names = list({key for key in metric_names})

        self.render(os.path.join(os.path.dirname(__file__), "experiment_explorer.html"), projects=projects, project=project, experiments=experiments, metric_names=metric_names)
