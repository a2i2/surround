import json
import tornado.web
import tornado.escape

class EditNotes(tornado.web.RequestHandler):
    def initialize(self, experiment_reader, experiment_writer):
        self.reader = experiment_reader
        self.writer = experiment_writer

    def get(self):
        project_name = self.get_argument("project_name", default=None)
        experiment = self.get_argument("experiment", default=None)

        if not project_name or not experiment:
            self.set_status(400)
            return

        try:
            exec_info = self.reader.pull_experiment_file(project_name, experiment, "execution_info.json")
            exec_info = json.loads(exec_info.decode('utf-8'))
            self.write("\n".join(exec_info["notes"]))
        except FileNotFoundError:
            self.set_status(404)

    def post(self):
        data = tornado.escape.json_decode(self.request.body)

        if "projectName" not in data or "notes" not in data or "experiment" not in data:
            self.set_status(400)
            return

        try:
            exec_info = self.reader.pull_experiment_file(data['projectName'], data['experiment'], "execution_info.json")
            exec_info = json.loads(exec_info.decode('utf-8'))
            exec_info['notes'] = data['notes']

            self.writer.push_experiment_file(data['projectName'], data['experiment'], "execution_info.json", json.dumps(exec_info, indent=4).encode('utf-8'))
        except FileNotFoundError:
            self.set_status(404)
