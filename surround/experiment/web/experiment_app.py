import tornado.web

from ..experiment_reader import ExperimentReader
from .project_explorer import ProjectExplorer
from .experiment_explorer import ExperimentExplorer
from .results import Results
from .view_logs import ViewLogs

class ExperimentApp(tornado.web.Application):
    def __init__(self, storage_url=None):
        reader = ExperimentReader(storage_url)

        handlers = [
            (r'/', ProjectExplorer, {'experiment_reader': reader}),
            (r'/experiment', ExperimentExplorer, {'experiment_reader': reader}),
            (r'/results', Results, {'experiment_reader': reader}),
            (r'/view_logs', ViewLogs, {'experiment_reader': reader}),
        ]

        tornado.web.Application.__init__(self, handlers)
