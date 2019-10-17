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

        projects = self.experiment_reader.list_projects()
        project = self.experiment_reader.get_project(project_name)
        experiment = self.experiment_reader.get_experiment(project_name, start_time)

        logs = []
        for log in experiment['logs']:
            match = re.compile(r"^([0-9\- ]+):([A-Z]+):([a-z_\.]+):(.*)", re.DOTALL).match(log)

            # If fails to match regex, add to previous message
            if not match and logs:
                logs[-1]['message'] += "<br />" + log
                continue

            timestamp = match.group(1)
            level = match.group(2)
            package = match.group(3)
            msg = match.group(4)

            logs.append({
                'timestamp': timestamp,
                'level': level,
                'package': package,
                'message': msg.replace('\n', '<br />')
            })

        self.render(os.path.join(os.path.dirname(__file__), "view_logs.html"), project_names=projects, project=project, experiment=experiment, logs=logs)
