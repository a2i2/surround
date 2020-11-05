import tornado.web

class Download(tornado.web.RequestHandler):
    def initialize(self, experiment_reader):
        self.reader = experiment_reader

    def get(self):
        project_name = self.get_argument("project_name", default=None)
        experiment = self.get_argument("experiment", default=None)

        if not project_name or not experiment:
            self.set_status(404)
            return

        # Construct a zip file of the experiment
        zip_file = self.reader.replicate(project_name, experiment, include_output=True)
        buf_size = 4096

        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=experiment-%s-%s.zip' % (project_name, experiment))

        while True:
            data = zip_file[:buf_size]
            zip_file = zip_file[buf_size:]

            if not data:
                break

            self.write(data)

        self.finish()
