import os
import re
import tornado.web

class ViewLogs(tornado.web.RequestHandler):
    def initialize(self, experiment_reader):
        self.experiment_reader = experiment_reader

    def get(self):
        project_name = self.get_argument("project_name", default=None)
        start_time = self.get_argument("experiment", default=None)

        if not project_name or not start_time:
            self.redirect("./", permanent=True)

        projects = self.experiment_reader.get_projects()
        project = self.experiment_reader.get_project(project_name)
        experiment = self.experiment_reader.get_experiment(project_name, start_time)

        log_files = self.experiment_reader.get_experiment_files(project_name, start_time, base_url="logs")
        if not log_files:
            log_files = []

        logs = []
        for log_file in log_files:
            timestamp = log_file[:26]
            log = self.experiment_reader.pull_experiment_file(project_name, start_time, "logs/%s" % log_file)

            log = re.compile(r"^([A-Z]+):([a-z_\.]+):(.*)", re.DOTALL).match(log.decode('utf-8'))
            level = log.group(1)
            package = log.group(2)
            msg = log.group(3)

            logs.append({
                'timestamp': timestamp,
                'level': level,
                'package': package,
                'message': msg
            })

        self.render(os.path.join(os.path.dirname(__file__), "view_logs.html"), projects=projects, project=project, experiment=experiment, logs=logs)
