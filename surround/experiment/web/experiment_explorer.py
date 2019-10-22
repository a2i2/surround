import os
import math
import tornado.web

class ExperimentExplorer(tornado.web.RequestHandler):
    def initialize(self, experiment_reader):
        self.experiment_reader = experiment_reader

    def get(self):
        project_name = self.get_argument("project_name", default=None)
        page = self.get_argument("page", default="1")

        try:
            page = int(page)
        except ValueError:
            self.redirect("./", permanent=True)
            return

        if not project_name:
            self.redirect("./", permanent=True)

        projects = self.experiment_reader.list_projects()
        project = self.experiment_reader.get_project(project_name)

        experiments = self.experiment_reader.list_experiments(project_name)
        experiments = sorted(experiments, reverse=True)

        if experiments:
            num_per_page = 10
            pages = list(range(1, math.ceil(len(experiments) / num_per_page) + 1))

            if page not in pages:
                page = pages[-1]

            if len(experiments) > num_per_page:
                index = (page - 1) * num_per_page
                experiments = experiments[index:index + num_per_page]
        else:
            pages = [1]

        self.render(os.path.join(os.path.dirname(__file__), "experiment_explorer.html"), project_names=projects, project=project, experiments=experiments, page=page, pages=pages)
