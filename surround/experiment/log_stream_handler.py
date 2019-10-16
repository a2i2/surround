import os
from logging import Handler, Formatter, getLogger
from datetime import datetime

class LogStreamHandler(Handler):
    def __init__(self, storage, experiment):
        super().__init__()
        self.storage = storage
        self.experiment = experiment
        self.count = 0
        self.setFormatter(Formatter("%(levelname)s:%(name)s:%(message)s"))

    def emit(self, record):
        msg = self.format(record)
        msg = "%s:%s" % (datetime.now().strftime("%Y-%m-%d %H-%M-%S-%f"), msg)

        # Append the log to a text file in the root of the project
        with open(os.path.join(self.experiment['project_root'], "log.txt"), "a+") as f:
            f.write("%s\n" % msg)

        # Remove us from the logger (so we don't capture logs from the push operation)
        root_logger = getLogger()
        root_logger.removeHandler(self)

        # Push the log file to experiment storage
        self.storage.push(
            "experimentation/%s/experiments/%s/log.txt" % (self.experiment['project_name'], self.experiment['time_started']),
            local_path=os.path.join(self.experiment['project_root'], "log.txt"), override_ok=True)

        # Add us back to the root logger
        root_logger.addHandler(self)
