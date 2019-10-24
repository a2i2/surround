import os
from logging import Handler, Formatter
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

        # Push a new text file to the logs folder in the experiment folder
        path = "experimentation/%s/experiments/%s/logs/%s_%i.txt" % (
            self.experiment['project_name'],
            self.experiment['time_started'],
            datetime.now().strftime("%Y-%m-%d %H-%M-%S-%f"),
            self.count)

        # Append the log to a text file in the root of the project
        with open(os.path.join(self.experiment['project_root'], "log.txt"), "a+") as f:
            f.write("%s\n" % msg)

        self.storage.push(path, bytes_data=msg.encode('utf-8'))
        self.count += 1
